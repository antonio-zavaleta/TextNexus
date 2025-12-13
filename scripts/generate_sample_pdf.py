from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, '20,000 Leagues Under the Sea', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def create_dummy_pdf(filename):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)

    # Content
    content = """
    The year 1866 was signalised by a remarkable incident, a mysterious and puzzling phenomenon, which doubtless no one has yet forgotten. Not to mention rumours which agitated the maritime population and excited the public mind, even in the interior of continents, seafaring men were particularly excited. Merchants, common sailors, captains of vessels, skippers, both of Europe and America, naval officers of all countries, and the Governments of several States on the two continents, were deeply interested in the matter.

    For some time past vessels had been met by "an enormous thing," a long object, spindle-shaped, occasionally phosphorescent, and infinitely larger and more rapid in its movements than a whale.

    The facts relating to this apparition (entered in various log-books) agreed in most respects as to the shape of the object or creature, the untiring rapidity of its movements, its surprising power of locomotion, and the peculiar life with which it seemed endowed. If it was a whale, it surpassed in size all those hitherto classified in science. Taking into consideration the mean of observations made at divers times rejecting the timid estimate of those who assigned to this object a length of two hundred feet, equally with the exaggerated opinions which set it down as a mile in width and three in length we might fairly conclude that this mysterious being surpassed greatly all dimensions admitted by the ichthyologists of the day, if it existed at all.
    """
    
    pdf.multi_cell(0, 10, content)
    
    pdf.ln(10)
    pdf.set_font('Times', 'B', 12)
    pdf.cell(0, 10, 'Notable Encounters:', 0, 1)
    pdf.set_font('Times', '', 12)
    
    # Simple Table-like structure
    pdf.cell(40, 10, 'Date', 1)
    pdf.cell(60, 10, 'Vessel', 1)
    pdf.cell(90, 10, 'Observation', 1)
    pdf.ln()
    
    encounters = [
        ('1866-07-20', 'Governor Higginson', 'Large object, 5 miles off'),
        ('1866-07-23', 'Columbus', 'Collision with unknown mass'),
        ('1866-08-20', 'Helvetia', 'Spotted phosphorescent lights')
    ]
    
    for date, vessel, obs in encounters:
        pdf.cell(40, 10, date, 1)
        pdf.cell(60, 10, vessel, 1)
        pdf.cell(90, 10, obs, 1)
        pdf.ln()

    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    pdf.output(filename)
    print(f"Successfully created: {filename}")

if __name__ == "__main__":
    create_dummy_pdf("tests/data/20k_leagues.pdf")
