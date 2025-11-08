Due to unforseen circumstances, we are not able to solve one of the bug therefore we submitted last minute with the important bug unsolved!
It is related to our advanced sorting algorithm to sort patient's priority medication by considering age, blood sugar level, blood pressure level (systolic and diastolic), with each parameters having their weigtage
(importance).
However, we are happy that we are able to solve it after a few hours of submission. This is the video link for the comprehensive proposed solution! 
This Github Repository basically keeps:
1) OCR
   -We utilize open source library tessaract OCR (trained with neural network) to recognize text. Then we draw grids on the paper to let OCR read the text on the grid on a specific data and convert it into JSON.
   -We then package it with streamlit so it can be run on cloud and serves as an app ( easy integration of phone taking photo and uploading immediately)
   -We use OCR taking from the inspiration of passport scanning as OCR saves all the hassle of keying in value one by one, and even when Wifi is not available, pictures can be taken and saved into phone and can be
   uploaded anytime when it is available.
   -This would ease the job of BHW.
   -Although Agentic AI is the trend now, we thought that OCR is suitable for Jagna's case as they need a easy to use and working solution instead of a complex one that provides unnecessary function.Of course,
   this could be implemented when they are more tech-savvy.
uitable 
2) Google Sheets
  -A database is crucial for a health data like this. However , considering the population of Jagnaited and their limited competency on technology, we still follow our principle of design mindset, to make it simple
  to use and necessary,to use what they already have (google form+sheets). When data expands, like there are more visits for each patients , we should migrate this to database.
  -Sorting algorithm would rank priority of medicine when demand is over supply while counting algorithm can count the amount of medication needed so it can be prepared by other stakeholders such as goverment.we 
  -Using Google App Script , we are able to automate these algorithms and Facebook Messenger API calls.
  -To run every function -> Extension -> Ap p Script -> Run ( It is now available to me only but let me know if you want to test it out, email is necessary!)

3) Messenger Bot
   -By collecting patients PSID (available when patient send a message to our Facebook Page: Health Record within 24 hours.
   -PSID is a specific ID for one Facebook user and one Facebook Page, so it can solve the issue of certain people not having national ID.
   -Running these scripts requires many permissions + page acess token+user token due to Meta's security.

Possible Improvements:

Reflection:

   
