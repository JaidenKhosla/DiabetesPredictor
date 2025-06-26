import React from "react";
import "./assets/stylesheets/Form.css"

type modelType = "linear" | "logistic" | "randomForest" | "polynomial";

interface FormData {
    gender: "Male" | "Female" | "Other";
    age: number;
    hypertension: number;
    heart_disease: number;
    smoking_history: "former" | "current" | "unknown" | "no info";
    bmi: number;
    HbA1c_level: number;
    blood_glucose_level: number;
}

const initialForm: FormData = {
    gender: "Male",
    age: 34,
    hypertension: 1,
    heart_disease: 1,
    smoking_history: "former",
    bmi: 34,
    HbA1c_level: 34,
    blood_glucose_level: 34,
}

export default function Form() {

    const [formData, setFormData] = React.useState<FormData>(initialForm);
    const [useModel, setModel] = React.useState<modelType>("randomForest") 
    const [hasDiabetes, setHasDiabetes] = React.useState<Number[]>([-1,-1]);
    const [debounce, setDebounce] = React.useState<boolean>(false);
    function sendReq(data: FormData){

        console.log(JSON.stringify(data));
        setDebounce(true);
        fetch("http://127.0.0.1:5000/generate", {
            method: "POST",
            headers: {
                "Content-Type" : "application/json"
            },
            body: JSON.stringify({"features": formData, "model": useModel})
        }).then(async response => {
            if(!response.ok)
                console.log(await response.status)
            const res = await response.json();
            setHasDiabetes(res.result);
        }).then((data)=>{
            console.log("Success!", data)
            setDebounce(false);
        }).catch(err => {
            console.error(err);
            setDebounce(false);
            setHasDiabetes([-2,-2])
        });
        
    }

    function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) {
        const { name, value } = e.target;
        e.target.value = value;

        setFormData(prev => ({
            ...prev,
            [name]: name === "age" || name === "hypertension" || name === "heart_disease" || name === "bmi" || name === "HbA1c_level" || name === "blood_glucose_level"
            ? Number(value)
            : value
        }))
    }

    return <div className='Form'>

        <label htmlFor='gender'>Gender</label>
        <select name='gender' value={formData.gender} onChange={handleChange}>
            <option value="Male">Male</option>
            <option value="Female">Female</option>
            <option value="Other">Other</option>
        </select>
        <label htmlFor='age'>Age</label>
        <input type='number' name='age' value={formData.age} placeholder='Age' onChange={handleChange} min={0}/>
        <label htmlFor='hypertension'>Hypertension</label>
        <select name='hypertension' value={formData.hypertension} onChange={handleChange}>
            <option value={0}>No</option>
            <option value={1}>Yes</option>
        </select>
        <label htmlFor='heart_disease'>Heart Disease</label>
        <select name='heart_disease' value={formData.heart_disease} onChange={handleChange}>
            <option value={0}>No</option>
            <option value={1}>Yes</option>
        </select>
        <label htmlFor='smoking_history'>Smoking History</label>
        <select name='smoking_history' value={formData.smoking_history} onChange={handleChange}>
            <option value="never">Never</option>
            <option value="former">Former</option>
            <option value="current">Current</option>
            <option value="unknown">Unknown</option>
        </select>
        <label htmlFor='bmi'>BMI</label>
        <input type='number' name='bmi' placeholder='BMI' value={formData.bmi} step='0.01' onChange={handleChange}/>
        <label htmlFor='HbA1c_level'>HbA1c Level</label>
        <input type='number' name='HbA1c_level' placeholder='HbA1c Level' value={formData.HbA1c_level} step='0.01' onChange={handleChange} min={0}/>
        <label htmlFor='blood_glucose_level'>Blood Glucose Level</label>
        <input type='number' name='blood_glucose_level' placeholder='Blood Glucose Level' step='0.01' value={formData.blood_glucose_level} onChange={handleChange} min={0}/>
        <label htmlFor="model">Model</label>
        <select name='model' value={useModel} onChange={(e)=>{setModel(e.target.value as modelType)}}>
            <option value="linear">Linear Regression</option>
            <option value="logistic">Logistic Regression</option>
            <option value="randomForest">Random Forest Regression</option>
            <option value="polynomial">Polynomial Regression</option>
        </select>
        <br></br>
        <button disabled={debounce} onClick={()=>{
            if(!debounce)
                sendReq(formData);
        }}>Do I have Diabetes?</button>
        <p>{hasDiabetes[0] === -2 ? "There seems to be an error. Please try again later." : hasDiabetes[0] === -1 ? "" : hasDiabetes[0] === 0 ? "You don't have diabetes." : "You have diabetes."}</p>
        <p>{hasDiabetes[0] === -1 || hasDiabetes[0] === -2 ? "" : hasDiabetes[0] === 0 ? `With a ${((1-Number(hasDiabetes[1]))*100).toFixed(3)}% accuracy.` : `With a ${(Number(hasDiabetes[1])*100).toFixed(3)}% accuracy.`}</p>
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