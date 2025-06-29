import React from "react";
import "./assets/stylesheets/Form.css"

type modelType = "ComplementNB" | "GaussianNB" | "MultinomialNB" | "RandomForest" | "SVC";

interface FormData {
    age: number;
    sex: number;
    cp: number;
    trestbps: number;
    chol: number;
    fbs: 1 | 0;
    restecg: 0|1|2;
    thalach: number;
    exang: 1 | 0;
    oldpeak: number;
    slope: number;
    ca: 0|1|2|3;
    thal: 0|1|2|3;
}

const initialForm: FormData = {
    age: 30,
    sex: 1,
    cp: 5,
    trestbps: 5,
    chol:5,
    fbs: 1,
    restecg: 2,
    thalach: 100,
    exang: 1,
    oldpeak: 3,
    slope: 5,
    ca: 3,
    thal: 3
}

export default function HeartDiseaseForm() {

    const [formData, setFormData] = React.useState<FormData>(initialForm);
    const [useModel, setModel] = React.useState<modelType>("RandomForest") 
    const [hasHeartDisease, setHasHeartDisease] = React.useState<Number[]>([-1,-1]);
    const [debounce, setDebounce] = React.useState<boolean>(false);
    function sendReq(data: FormData){

        console.log(JSON.stringify(data));
        setDebounce(true);
        fetch("http://127.0.0.1:5000/generate", {
            method: "POST",
            headers: {
                "Content-Type" : "application/json"
            },
            body: JSON.stringify({"features": formData, "model": useModel, "category": "HeartDisease"})
        }).then(async response => {
            if(!response.ok)
                console.log(await response.status)
            const res = await response.json();
            setHasHeartDisease(res.result);
        }).then((data)=>{
            console.log("Success!", data)
            setDebounce(false);
        }).catch(err => {
            console.error(err);
            setDebounce(false);
            setHasHeartDisease([-2,-2])
        });
        
    }

    function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
        const { name, value } = e.target;
        e.target.value = value;

        setFormData(prev => ({
            ...prev,
            [name]: Number(value)
        }))
    }

    return <div className='Form'>

        <label htmlFor='sex'>Gender</label>
        <select name='sex' value={formData.sex} onChange={handleChange}>
            <option value={1}>Male</option>
            <option value={0}>Female</option>
            <option value={0.5}>Other</option>
        </select>

        <label htmlFor='age'>Age</label>
        <input type='number' name='age' value={formData.age} placeholder='Age' onChange={handleChange} min={0}/>

        <label htmlFor='chest_pain'>Chest Pain</label>
        <select name='chest_pain' value={formData.cp} onChange={handleChange}>
            <option value={0}>Typical Angina</option>
            <option value={1}>Atypical Angina</option>
            <option value={2}>Non-anginal Pain</option>
            <option value={3}>Asymptomatic</option>
        </select>

        <label htmlFor='trestbps'>Resting Blood Pressure</label>
        <input type="number" name="trestbps" value={formData.trestbps} onChange={handleChange} min={0}/>

        <label htmlFor="chol">Cholestrol</label>
        <input type="number" name="chol" value={formData.chol} onChange={handleChange} min={0}/>
        
        <label htmlFor="fbs">Fasting Blood Sugar greater than 120 mg/dl</label>
        <select name="fbs" value={formData.fbs} onChange={handleChange}>
            <option value={1}>Yes</option>
            <option value={0}>No</option>
        </select>

        <label htmlFor="restecg">Resting Electrocardiographic Results</label>
        <select name="restecg" value={formData.restecg} onChange={handleChange}>
            <option value={0}>Normal</option>
            <option value={1}>Have a ST-T Wave Abnormality</option>
            <option value={2}>Showing Probable or Definite Left Ventricular Hypertrophy by Estes' Criteria</option>
        </select>

        <label htmlFor="thalach">Maximum Heart Rate Achieved</label>
        <input type="number" name="thalach" min={0} value={formData.thalach} onChange={handleChange}/>

        <label htmlFor="exang">Exercise Induced Angina</label>
        <select name="exang" value={formData.exang} onChange={handleChange}>
            <option value={1}>Yes</option>
            <option value={0}>No</option>
        </select>

        <label htmlFor="oldpeak">ST Depression Induced by Exercise</label>
        <input type="number" name="oldpeak" min={0} value={formData.oldpeak} onChange={handleChange}/>

        <label htmlFor="slope">The Slope of The Peak Exercise ST Segment</label>
        <select name="slope" value={formData.slope} onChange={handleChange}>
            <option value={0}>Upsloping</option>
            <option value={1}>Flat</option>
            <option value={2}>Downsloping</option>
        </select>
   
        <label htmlFor="ca">Number of Major Vessels Colored by Flourosopy</label>
        <select name="ca" value={formData.ca} onChange={handleChange}>
            <option value={0}>0</option>
            <option value={1}>1</option>
            <option value={2}>2</option>
            <option value={3}>3</option>
        </select>

        <label htmlFor="thal">Thal</label>
        <select name="thal" value={formData.thal} onChange={handleChange}>
            <option value={0}>Not Known</option>
            <option value={1}>Fixed Defect</option>
            <option value={2}>Normal</option>
            <option value={3}>Reversable Defect</option>
        </select>

        <label htmlFor="model">Model</label>
        <select name='model' value={useModel} onChange={(e)=>{setModel(e.target.value as modelType)}}>
            <option value="ComplementNB">Complement Naive Bayes</option>
            <option value="GaussianNB">Gaussian Naive Bayes</option>
            <option value="MultinomialNB">Multinomial Naive Bayes</option>
            <option value="RandomForest">Random Forest</option>
            <option value="SVC">Support Vector Classifier</option>
        </select>

        <br></br>
        <button disabled={debounce} onClick={()=>{
            if(!debounce)
                sendReq(formData);
        }}>Do I have Heart Disease?</button>
        <p>{hasHeartDisease[0] === -2 ? "There seems to be an error. Please try again later." : hasHeartDisease[0] === -1 ? "" : hasHeartDisease[0] === 0 ? "You don't have Heart Disease." : "You have Heart Disease."}</p>
        <p>{hasHeartDisease[0] === -1 || hasHeartDisease[0] === -2 ? "" : hasHeartDisease[0] === 0 ? `With a ${((1-Number(hasHeartDisease[1]))*100).toFixed(3)}% accuracy.` : `With a ${(Number(hasHeartDisease[1])*100).toFixed(3)}% accuracy.`}</p>
    </div>


}




// {
//     \"gender\" : \"Male\",
//     \"age\" : 12.0,
//     \"hypertension\": 1,
//     \"heart_disease\": 1,
//     \"smoking_history\": \"current\",
//     \"bmi\" : 23.86,
//     \"HbA1c_level\": 4.8,
//     \"blood_glucose_level\": 157.0
// }