"""
Sample medical documents for demonstration and testing.
These cover common clinical topics: hypertension, diabetes, drug interactions, and diagnostics.
"""

SAMPLE_MEDICAL_DOCUMENTS = [
    {
        "title": "JNC 8 Guidelines: Management of Hypertension in Adults",
        "url": "https://jamanetwork.com/journals/jama/fullarticle/1791497",
        "metadata": {
            "source_type": "guideline",
            "category": "cardiology",
            "year": "2024",
        },
        "content": """# JNC 8 Guidelines: Management of Hypertension in Adults

## Key Recommendations

### Blood Pressure Thresholds for Pharmacologic Treatment
- In the general population aged ≥60 years, initiate pharmacologic treatment at systolic blood pressure (SBP) ≥150 mmHg or diastolic blood pressure (DBP) ≥90 mmHg, with a treatment goal of SBP <150 mmHg and DBP <90 mmHg.
- In the general population <60 years, initiate pharmacologic treatment at DBP ≥90 mmHg, with a goal of DBP <90 mmHg.
- In the general population <60 years, initiate pharmacologic treatment at SBP ≥140 mmHg, with a goal of SBP <140 mmHg.
- In patients aged ≥18 years with chronic kidney disease (CKD), initiate pharmacologic treatment at SBP ≥140 mmHg or DBP ≥90 mmHg, with a goal of SBP <140 mmHg and DBP <90 mmHg.
- In patients aged ≥18 years with diabetes, initiate pharmacologic treatment at SBP ≥140 mmHg or DBP ≥90 mmHg, with a goal of SBP <140 mmHg and DBP <90 mmHg.

### Recommended Medications
- In the general nonblack population (including those with diabetes): initial treatment should include a thiazide-type diuretic, calcium channel blocker (CCB), angiotensin-converting enzyme inhibitor (ACEI), or angiotensin receptor blocker (ARB).
- In the general black population (including those with diabetes): initial treatment should include a thiazide-type diuretic or CCB.
- In patients aged ≥18 years with CKD: initial or add-on treatment should include an ACEI or ARB to improve kidney outcomes, regardless of race or diabetes status.

### Hypertension Management in CKD Patients
- Target blood pressure in CKD patients: <140/90 mmHg.
- First-line agents: ACE inhibitors or ARBs are recommended due to their renoprotective effects.
- Monitor serum creatinine and potassium levels within 2-4 weeks of initiating or increasing ACEI/ARB therapy.
- If GFR declines >30% from baseline, consider alternative agents and evaluate for renal artery stenosis.
- Combination therapy: If target BP is not achieved with one drug, add a second drug from the recommended classes before maximizing the dose of the initial drug.

### Lifestyle Modifications
- Weight reduction for overweight or obese patients (BMI goal <25 kg/m²)
- Adopt DASH eating plan: rich in fruits, vegetables, and low-fat dairy products with reduced saturated and total fat
- Dietary sodium reduction to no more than 2,400 mg/day (ideally 1,500 mg/day)
- Regular aerobic physical activity (at least 30 minutes per day, most days of the week)
- Moderate alcohol consumption (no more than 2 drinks/day for men, 1 drink/day for women)
""",
    },
    {
        "title": "ADA Standards of Care in Diabetes — 2024",
        "url": "https://diabetesjournals.org/care/issue/47/Supplement_1",
        "metadata": {
            "source_type": "guideline",
            "category": "endocrinology",
            "year": "2024",
        },
        "content": """# ADA Standards of Care in Diabetes — 2024

## Diagnostic Criteria for Diabetes
- Fasting plasma glucose (FPG) ≥126 mg/dL (7.0 mmol/L), OR
- 2-hour plasma glucose ≥200 mg/dL (11.1 mmol/L) during oral glucose tolerance test (OGTT), OR
- HbA1c ≥6.5% (48 mmol/mol), OR
- Random plasma glucose ≥200 mg/dL (11.1 mmol/L) with classic symptoms of hyperglycemia.

## Glycemic Targets
- A reasonable HbA1c goal for many nonpregnant adults is <7.0% (53 mmol/mol).
- More stringent goals (e.g., <6.5%) may be appropriate for selected patients if achievable without significant hypoglycemia.
- Less stringent goals (e.g., <8%) may be appropriate for patients with a history of severe hypoglycemia, limited life expectancy, advanced complications, or extensive comorbidities.

## Pharmacologic Management of Type 2 Diabetes
- Metformin remains the preferred initial pharmacologic agent for type 2 diabetes.
- For patients with established atherosclerotic cardiovascular disease (ASCVD), heart failure, or CKD: consider adding a GLP-1 receptor agonist or SGLT2 inhibitor with demonstrated cardiovascular or renal benefit, independent of HbA1c.
- GLP-1 receptor agonists (e.g., semaglutide, liraglutide, dulaglutide) have shown cardiovascular benefit in clinical trials.
- SGLT2 inhibitors (e.g., empagliflozin, dapagliflozin, canagliflozin) reduce heart failure hospitalization and CKD progression.
- Insulin therapy should be considered when HbA1c remains above target despite optimal oral/injectable therapy.

## Blood Pressure Management in Diabetes
- Blood pressure should be measured at every clinical visit.
- Target BP: <130/80 mmHg for patients with diabetes and hypertension at higher cardiovascular risk.
- First-line agents: ACE inhibitors or ARBs, particularly in patients with albuminuria.
- Combination therapy is often required to achieve BP targets.

## Screening Recommendations
- Type 2 diabetes screening in asymptomatic adults should begin at age 35 years, or earlier in individuals who are overweight/obese with additional risk factors.
- Screen for diabetic retinopathy at diagnosis of type 2 diabetes, then at least every 1-2 years.
- Screen for diabetic nephropathy annually with urinary albumin-to-creatinine ratio and estimated GFR.
- Comprehensive foot exam at least annually for all patients with diabetes.
""",
    },
    {
        "title": "Common Drug Interactions in Clinical Practice",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK441917/",
        "metadata": {
            "source_type": "drug_reference",
            "category": "pharmacology",
            "year": "2024",
        },
        "content": """# Common Drug Interactions in Clinical Practice

## Warfarin Interactions
**Warfarin** is one of the most commonly involved drugs in clinically significant interactions.

### Drugs that INCREASE warfarin effect (increased bleeding risk):
- **Amiodarone**: Inhibits CYP2C9 metabolism of warfarin. Reduce warfarin dose by 30-50% when initiating amiodarone. Monitor INR weekly for the first 4 weeks.
- **Fluconazole/Voriconazole**: Strong CYP2C9 inhibitors. Significantly increase warfarin levels. Reduce warfarin dose by 25-50%.
- **Metronidazole**: Inhibits CYP2C9. Monitor INR closely; reduce warfarin dose as needed.
- **Ciprofloxacin**: Inhibits CYP1A2 metabolism. Monitor INR within 3-5 days of initiation.
- **NSAIDs** (ibuprofen, naproxen): Increase bleeding risk through antiplatelet effect and GI mucosal damage. Avoid combination if possible.

### Drugs that DECREASE warfarin effect:
- **Rifampin**: Potent CYP2C9 inducer. Can reduce warfarin effect by up to 70%. Avoid combination; use alternative antibiotic.
- **Carbamazepine**: CYP inducer. Monitor INR and increase warfarin dose as needed.
- **St. John's Wort**: Induces CYP3A4 and CYP2C9. Advise patients to avoid.

## Statin Interactions
- **Simvastatin + Amiodarone**: Maximum simvastatin dose 20 mg/day due to increased risk of rhabdomyolysis.
- **Statins + Macrolides** (erythromycin, clarithromycin): Increased statin levels via CYP3A4 inhibition. Use azithromycin as alternative.
- **Statins + Grapefruit juice**: CYP3A4 inhibition. Advise patients to limit grapefruit consumption with simvastatin and atorvastatin.

## ACE Inhibitor / ARB Interactions
- **ACEi/ARB + Potassium-sparing diuretics** (spironolactone): Risk of hyperkalemia. Monitor potassium levels closely.
- **ACEi/ARB + NSAIDs**: Reduced antihypertensive effect and increased risk of acute kidney injury. Monitor renal function and blood pressure.
- **Dual RAAS blockade** (ACEi + ARB or + direct renin inhibitor): Increased risk of hyperkalemia, hypotension, and renal impairment. Generally contraindicated.

## Metformin Interactions
- **Metformin + Contrast media**: Risk of lactic acidosis. Hold metformin for 48 hours before and after iodinated contrast. Check renal function before resuming.
- **Metformin + Alcohol**: Increased risk of lactic acidosis. Advise moderation.

## QT-Prolonging Drug Combinations
Avoid combining QT-prolonging drugs. High-risk combinations include:
- Amiodarone + Fluoroquinolones (ciprofloxacin, levofloxacin)
- Haloperidol + Ondansetron
- Macrolides + Antipsychotics
Monitor ECG when combinations are unavoidable.
""",
    },
    {
        "title": "Differential Diagnosis of Chest Pain in Adults",
        "url": "https://www.aafp.org/pubs/afp/issues/2020/1115/p566.html",
        "metadata": {
            "source_type": "clinical_reference",
            "category": "emergency_medicine",
            "year": "2024",
        },
        "content": """# Differential Diagnosis of Chest Pain in Adults

## Cardiac Causes

### Acute Coronary Syndrome (ACS)
- **Presentation**: Substernal chest pressure or squeezing, may radiate to left arm, jaw, or back. Associated with diaphoresis, nausea, dyspnea.
- **Risk Factors**: Age >45 (men), >55 (women), hypertension, diabetes, hyperlipidemia, smoking, family history of premature CAD.
- **Diagnosis**: Serial troponins (high-sensitivity preferred), 12-lead ECG, risk stratification with HEART score.
- **Red Flags**: ST-segment elevation on ECG → immediate catheterization. New left bundle branch block.

### Aortic Dissection
- **Presentation**: Sudden, severe "tearing" chest pain radiating to the back. May present with pulse deficit, blood pressure differential between arms.
- **Risk Factors**: Hypertension, Marfan syndrome, bicuspid aortic valve, recent cardiac surgery.
- **Diagnosis**: CT angiography of the chest (gold standard). D-dimer may help rule out if low clinical suspicion.
- **Emergency**: Surgical emergency for Type A dissection (ascending aorta).

### Pericarditis
- **Presentation**: Sharp, pleuritic chest pain worse with inspiration and lying supine, improved with leaning forward.
- **Diagnosis**: ECG showing diffuse ST elevation and PR depression. Echocardiogram to assess for pericardial effusion.

## Pulmonary Causes

### Pulmonary Embolism (PE)
- **Presentation**: Acute dyspnea, pleuritic chest pain, tachycardia, hemoptysis. May present with unilateral leg swelling (DVT).
- **Risk Factors**: Recent surgery, immobilization, malignancy, oral contraceptive use, prior VTE, thrombophilia.
- **Diagnosis**: Use Wells score for pre-test probability. D-dimer for low-probability cases. CT pulmonary angiography (CTPA) for definitive diagnosis.
- **Treatment**: Anticoagulation (heparin → warfarin or DOAC). Consider thrombolysis for massive PE with hemodynamic instability.

### Pneumothorax
- **Presentation**: Sudden onset of unilateral chest pain and dyspnea. Decreased breath sounds on affected side.
- **Risk Factors**: Tall, thin males, smoking, underlying lung disease (COPD, cystic fibrosis), mechanical ventilation.
- **Diagnosis**: Chest X-ray (upright, in expiration). CT for small pneumothoraces.

## Gastrointestinal Causes

### Gastroesophageal Reflux Disease (GERD)
- **Presentation**: Burning substernal pain (heartburn), worse after meals and lying down. May mimic cardiac chest pain.
- **Diagnosis**: Trial of PPI therapy. Upper endoscopy for alarm symptoms (dysphagia, weight loss, anemia).
- **Key Differentiator**: Pain relieved by antacids. No ECG changes. Negative troponin.

### Esophageal Spasm
- **Presentation**: Intense squeezing chest pain that may be indistinguishable from angina. May be triggered by hot or cold foods.
- **Diagnosis**: Esophageal manometry. Barium swallow may show "corkscrew esophagus."

## Musculoskeletal Causes

### Costochondritis
- **Presentation**: Reproducible chest wall tenderness on palpation, typically at costochondral junctions.
- **Diagnosis**: Clinical diagnosis. Pain reproduced by palpation. No imaging usually needed.
- **Treatment**: NSAIDs, reassurance. Usually self-limited.
""",
    },
    {
        "title": "KDIGO 2024 Clinical Practice Guideline for CKD Management",
        "url": "https://kdigo.org/guidelines/ckd-evaluation-and-management/",
        "metadata": {
            "source_type": "guideline",
            "category": "nephrology",
            "year": "2024",
        },
        "content": """# KDIGO 2024 Clinical Practice Guideline for Chronic Kidney Disease

## CKD Staging
- **Stage 1** (G1): GFR ≥90 mL/min/1.73 m² — Normal or high, with evidence of kidney damage
- **Stage 2** (G2): GFR 60-89 — Mildly decreased
- **Stage 3a** (G3a): GFR 45-59 — Mildly to moderately decreased
- **Stage 3b** (G3b): GFR 30-44 — Moderately to severely decreased
- **Stage 4** (G4): GFR 15-29 — Severely decreased
- **Stage 5** (G5): GFR <15 — Kidney failure

## Blood Pressure Management in CKD
- Target systolic BP: <120 mmHg when tolerated (based on SPRINT trial data).
- First-line agents: ACE inhibitors or ARBs, especially with albuminuria >30 mg/g.
- Avoid dual RAAS blockade (ACEi + ARB) due to increased risk of adverse effects.
- SGLT2 inhibitors are recommended for patients with CKD and type 2 diabetes (GFR ≥20 mL/min) to slow CKD progression.
- Finerenone (nonsteroidal mineralocorticoid receptor antagonist) is recommended for patients with type 2 diabetes and CKD with albuminuria.

## Glycemic Management in CKD with Diabetes
- HbA1c target: individualized, generally <7% for most patients.
- Metformin: reduce dose when GFR 30-44; discontinue when GFR <30.
- SGLT2 inhibitors: can be initiated at GFR ≥20 mL/min; continue until dialysis or transplantation.
- GLP-1 receptor agonists: preferred add-on therapy for additional glycemic control and cardiovascular benefit.
- Insulin dosing: may need reduction as GFR declines (decreased renal clearance of insulin).

## Anemia Management
- Evaluate for iron deficiency before initiating erythropoiesis-stimulating agents (ESAs).
- Target hemoglobin: 10-11.5 g/dL with ESA therapy. Avoid exceeding 13 g/dL.
- Iron supplementation: IV iron preferred for dialysis patients.

## Mineral and Bone Disorder
- Monitor calcium, phosphorus, PTH, and vitamin D levels regularly.
- Phosphate management: dietary phosphate restriction, phosphate binders if needed.
- Vitamin D supplementation for deficiency.
""",
    },
]
