import re


text = '''Here are five possible scenarios that could happen after Shell completes the restart of operations at the Pierce Field in the UK North Sea after a major redevelopment to enable gas production:

- Scenario 1: Shell and Ithaca Energy enjoy increased revenues and profits from the Pierce field, which produces more than twice the amount of oil equivalent per day than before the redevelopment. The project also extends the life of the field by more than 20 years, providing a stable source of income for both companies. The gas produced at the field helps meet the UK's energy demand and reduces its reliance on imports. The project is hailed as a success story for the UK North Sea industry and a model for future developments.
- Scenario 2: Shell and Ithaca Energy face technical challenges and operational delays at the Pierce field, which affect the production and export of gas and oil. The FPSO vessel Haewene Brim, which was modified to handle gas production, suffers from mechanical failures and requires frequent maintenance. The new subsea gas export line also encounters problems with leaks, corrosion and blockages. The project fails to deliver the expected production levels and costs escalate significantly. The project is criticized as a risky and costly venture that jeopardizes the UK's energy security and environmental goals.
- Scenario 3: Shell and Ithaca Energy experience a major accident at the Pierce field, which results in a fire, explosion or oil spill. The incident causes injuries or fatalities to workers on board the FPSO vessel or nearby platforms. The incident also damages the subsea infrastructure and disrupts the production and export of gas and oil. The incident triggers an investigation by regulators and authorities, who impose fines, penalties and sanctions on both companies. The project is condemned as a disaster for the UK North Sea industry and a threat to public health and safety.
- Scenario 4: Shell and Ithaca Energy face competition and pressure from other players in the UK North Sea market, who offer cheaper or cleaner alternatives to gas and oil. The demand for gas and oil declines as consumers switch to renewable energy sources or electric vehicles. The prices of gas and oil also drop due to oversupply or geopolitical factors. The project becomes less profitable and attractive for both companies, who struggle to recover their investment costs and maintain their market share. The project is challenged as a short-sighted and unsustainable solution that ignores the UK's climate change commitments.
- Scenario 5: Shell and Ithaca Energy leverage their experience and expertise from the Pierce field to pursue new opportunities and partnerships in the UK North Sea region, which offer potential for further growth and innovation. The project enables both companies to acquire new skills, technologies and capabilities that enhance their competitiveness and efficiency. The project also strengthens their relationships with stakeholders, such as regulators, suppliers, customers and communities. The project is recognized as a catalyst for positive change and transformation in the UK North Sea industry.'''



test = [item for item in text.split("\n") if item != ""]


test = [1,2,3,4,5,6,7,8]
print(test[2:4])
