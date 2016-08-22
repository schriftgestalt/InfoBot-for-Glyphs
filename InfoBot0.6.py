#This script displays font info and then writes a PDF
import datetime
import unicodedata
from GlyphsApp import *
from robofab.world import *
from robofab.interface.all.dialogs import Message


#Clock
def clock():
    from datetime import datetime #timestamp will be drawn and used for filenames
    global timestamp
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4] #see function strftime in Python documentation
clock()

#Output Format
page_format = [842, 595]
#global variables
page_width = page_format[0]
page_height = page_format[1]
page_num = 0
scale_round = 0

#Chooing Fonts
current_font = Glyphs.font
#print(current_font)
#print current_font.familyName
current_font_filepath = current_font.filepath

#fontname = current_font.info.postscriptFullName #postscript name as string
#if fontname is None: 
    #Message("No postscript name given!") #alert if font info is not complete
if current_font is None: 
    Message("Open fonts you want to test first.")   #gives error message if no font is currently open 
    

#First Page
def firstPage():
    newPage(page_format[0], page_format[1]) #General Info Page
    fontSize(50)
    font("System Font Regular") #font used to display info
    text("Font Family:", (75, 420))
    text(current_font.familyName, (75, 360))


def MasterInfo():   
    for i in range (0, 30):
        try:
            print "Name" + ":" + " " + current_font.masters[i].name
            print "id" + ":" + " " + current_font.masters[i].id
            print "weight" + ":" + " " + current_font.masters[i].weight
            print "width" + ":" + " " + current_font.masters[i].width
            print current_font.masters[i].weightValue #object type: Float
            print current_font.masters[i].widthValue #object type: Float
            print current_font.masters[i].customName
            print current_font.masters[i].customValue
            print current_font.masters[i].italicAngle
        
        except AttributeError:
            number_fonts = str(i)
            print ("Total number of masters in font:" + " " + number_fonts)
            break


def drawInfo(): #Font Name, Designer and Glyphname on every page
    font("System Font Bold")
    fontSize(10)
    
    text(current_font.familyName + " " + "by" + " " + str(current_font.designer), (0, 0))
    
    glyph_name = current_glyph.name #new variable because to avoid conflict and confusion
    font("System Font Light")
    
    translate(0, - 12)
    
    uni_glyph = current_glyph.string
    print current_glyph.string
    try:
        text(unicodedata.name(uni_glyph), (0, 0))
    except:
        print 'No Name'
    
    translate(0, - 12)

    text(glyph_name, (0, 0))
    
    translate(0, - 12)
    
    text('0x' + current_font.glyphs['A'].unicode, (0, 0))
    

def getScaleX(page_width):
    global scale_round
    glyphlayers_width = 0
    widthlist= []

    for i in range (len(current_font.glyphs)): #iterates glyphs
        current_glyph = current_font.glyphs[i]
	        
        glyphlayers_width = 0    
        for i in range (len(current_glyph.layers)): #iterates layers
	        #print current_glyph.layers[i].bounds.size.width
	        
            glyphlayers_width = glyphlayers_width + current_glyph.layers[i].bounds.size.width #adds x values of bounding boxes
	        
        #print glyphlayers_width
        #print current_glyph
        widthlist.append(glyphlayers_width)
	    
	#print widthlist
    maxvalue = max(widthlist)
    #print maxvalue
    scaleraw = page_width / maxvalue

    #print scaleraw
    scale_round = round(scaleraw, 3)
    return scale_round

def drawLayers(): #draws all Layers of current_glyph
    global scale_round
    scale(scale_round)
    for i in range(len(current_glyph.layers)): #iterates Layers
        
        if len(current_glyph.layers[i].components) > 0: #Checks for components and decomposes
            current_glyph.layers[i].decomposeComponents()
            #print 'components decomposed'
        
        
        thisLayer = current_glyph.layers[i]
        
        #draws line at left side of bounding box
        stroke(0)
        x_line_start = thisLayer.bounds.origin.x
        y_line_start = thisLayer.bounds.origin.y
        line((x_line_start, y_line_start), (x_line_start, y_line_start + thisLayer.bounds.size.height))
               
        translate(thisLayer.LSB, 0)
        drawPath(thisLayer.bezierPath)
        translate(thisLayer.RSB, 0)
        
        #draws line at right side of bounding box
        stroke(0)
        x_line_start = thisLayer.bounds.origin.x + thisLayer.bounds.size.width
        y_line_start = thisLayer.bounds.origin.y
        line((x_line_start, y_line_start), (x_line_start, y_line_start + thisLayer.bounds.size.height))
        
        translate(thisLayer.bounds.size.width)
        translate(300)
        
        
def inputTeststring(): #iterates through layers and calls function drawWord
    global scale_round
    for i in range(len(current_font.masters)):
        leading = current_font.masters[i].xHeight * scale_round/3
        current_master = current_font.masters[i]
        save()
        drawWord(u'Handgloves', i, current_master) #current_font.familyName
        restore()
        #translate(0, -140)
        translate(0, - current_font.masters[i].capHeight * scale_round/2 - leading)
        i = i+1
        #print current_master
    return current_master
    
       
def drawWord(teststring,layer, current_master): #takes String input and draws it in selected weight
    
    weight_select = layer
    save()
    global scale_round
    scale(scale_round / 2)
        
    for c, item in enumerate(teststring):
        glyph_name = Glyphs.glyphInfoForUnicode(ord(item)).name
        thisLetter = current_font.glyphs[glyph_name]
        thisLetter.layers[weight_select].decomposeComponents()
        last_letter_name = Glyphs.glyphInfoForUnicode(ord(teststring[c-1])).name
        lastLetter = current_font.glyphs[last_letter_name]
        
        if c >= 1: #apply kerning from the second run on, would otherwise compare glyph corresponding to last letter of teststring!
            kerning = thisLetter.layers[weight_select].rightKerningForLayer_(lastLetter.layers[weight_select])    
        else:
            kerning = 0
            
        
        if kerning > 10000: #lowpass to filter out max values for non-existing kerning data
                kerning = 0
        #print thisLetter

        if thisLetter == current_font.glyphs['space' or 'nbspace' or 'thinspace']:
            translate(thisLetter.layers[weight_select].width, 0)
        else:
            drawPath(thisLetter.layers[weight_select].bezierPath) 
            translate(thisLetter.layers[weight_select].width) 

        
def drawPagina(): #draws Pagenumber
    fontSize(8)
    font("System Font Regular") #font used to display Number
    text(str(page_num), (0,0))


firstPage()
newPage()

getScaleX(page_width)

for i in range(len(current_font.glyphs)):
    current_glyph = current_font.glyphs[i]
    save()
    translate(20, page_height - page_height/ 3)
    drawLayers()
    restore()
    save()
    translate(page_width -30, page_height-20)
    drawPagina()
    restore()
    save()
    translate(20, page_height -20)
    drawInfo()
    restore()
    save()
    translate(20, page_height/2)
    scale(0.5)
    inputTeststring()
    restore()
    newPage()
    page_num = page_num +1
   
    
#print f.keys()
 
# find unicodes for each glyph by using the postscript name:


savetime = timestamp.replace(" ", "_") [:-3] #replaces space, cuts milliseconds
timestamp_save = savetime.replace(":", "")
fontname = current_font.familyName.replace(" ", "_") #takes spacing out of fontname
saveImage("~/Desktop/InfoBot" + "_" + fontname + "_" + timestamp_save + ".pdf")


current_font.close(True)
Glyphs.open(current_font_filepath)