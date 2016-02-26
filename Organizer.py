import wx
import datetime
from pytz import timezone
from pytz import all_timezones
import time
import math

class Frame(wx.Frame):
    def __init__(self, parent, title, windowWidth, windowHeight):
        super(Frame, self).__init__(parent, title=title, 
            size=(windowWidth, windowHeight), style=wx.NO_BORDER)# | wx.STAY_ON_TOP)

        self.justLoading = True
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.mouseOver = True
        self.secondColor = (255, 0, 0)
        self.minuteColor = (255, 255, 255)
        self.hourColor = (255, 255, 255)
        self.tickColor = (255, 255, 255)
        self.secondThick = 2
        self.minuteThick = 4
        self.hourThick = 4
        self.tickThick = 2
        self.secondLength = 50
        self.minuteLength = 50
        self.hourLength = .5*self.minuteLength
        self.clockMargin = 15
        self.clockTickLength = 10
        self.clockTickInnerMargin = 8
        self.clockWidth = (self.minuteLength*2) + (self.clockTickLength*2) + (self.clockTickInnerMargin*2)
        self.clockHeight = self.clockWidth
        self.clockX = (self.minuteLength) + (self.clockTickLength) + (self.clockTickInnerMargin) + self.clockMargin

        self.thisMonthCalDayColor = (255,255,255)
        self.otherMonthCalDayColor = (96,96,96)
        self.calTodayColor = (255,0,0)
        self.black = (0,0,0) 
        #self.display_width = int(3*(self.clockWidth+self.clockMargin))+self.clockMargin
        #self.display_height = 768

        self.bgColorMouseOver = (15, 15, 15)
        self.fgColorMouseOver = (255, 255, 255)
        self.bgColorMouseAway = (15, 15, 15)
        #self.fgColorMouseAway = (255, 255, 255)
        
        self.SetBackgroundColour(self.bgColorMouseOver)
        self.mostOpaqueLevel = 254 #254
        self.leastOpaqueLevel = 212 #212
        self.alphaTransparency = self.leastOpaqueLevel
        self.transparencyChangeSpeed = 1000
        self.transparencyChangeAmount = 1
        self.Centre()
        self.Show()
        self.SetBackgroundColour(self.bgColorMouseOver)
        self.displayTitleBar = False
        self.tzArray = ['America/Los_Angeles', 'America/New_York', 'Europe/London']
        self.tzDescArray = ["Seattle", "New York", "London"]
        self.changeAlpha_timer = wx.Timer(self)
        self.changeAlpha_timer.Start(self.transparencyChangeSpeed)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.mouseAway)
        self.Bind(wx.EVT_ENTER_WINDOW, self.mouseReturn)
        self.Bind(wx.EVT_LEFT_DCLICK, self.toggleTitleBar)
        self.Bind(wx.EVT_CLOSE, self.closeWindow )
        self.Bind(wx.EVT_MOTION, self.mouseMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.leftDown)
        self.Bind(wx.EVT_TIMER, self.drawClocks)

        self.drawCalendar()
        self.drawClockText()

        self.lastMouseClickPos = (0,0)
        self.justLoading = False

        #for zone in all_timezones:
        #    print zone


    def selectTimeZone(self):
        if self.justLoading == False:
            listOfAvailableTimeZones = []
            for zone in all_timezones:
                listOfAvailableTimeZones.append(zone)

            chooseOneBox = wx.SingleChoiceDialog(None, "What time zone should this clock show?", "Time Zone Selection", listOfAvailableTimeZones)
            if chooseOneBox.ShowModal() == wx.ID_OK:
                selTimeZone = chooseOneBox.GetStringSelection()
        
    def drawClockText(self):
        dc = wx.ClientDC(self)
        dc.SetFont(wx.Font(pointSize = 16, family = wx.DECORATIVE, style = wx.NORMAL, weight = wx.NORMAL))#, faceName = 'Consolas'))

        self.timeZoneCityLabel1 = wx.StaticText(self, -1, self.tzDescArray[0])
        self.timeZoneCityLabel2 = wx.StaticText(self, -1, self.tzDescArray[1])
        self.timeZoneCityLabel3 = wx.StaticText(self, -1, self.tzDescArray[2])

        self.timeZoneCityLabel1.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))#, faceName = 'Consolas'))
        self.timeZoneCityLabel1.SetForegroundColour(self.fgColorMouseOver)
        self.timeZoneCityLabel2.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.timeZoneCityLabel2.SetForegroundColour(self.fgColorMouseOver)
        self.timeZoneCityLabel3.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.timeZoneCityLabel3.SetForegroundColour(self.fgColorMouseOver)

        #CENTER ALIGN NOW THAT TEXT HAS BEEN DRAWN AND LENGTH IS KNOWN
        w,h = dc.GetTextExtent(self.tzDescArray[0])
        self.timeZoneCityLabel1.SetPosition((int(int((0*3*(self.clockWidth+self.clockMargin))/float(3)))+self.clockX-w/2, int(self.clockHeight / float(4))))
        w,h = dc.GetTextExtent(self.tzDescArray[1])
        self.timeZoneCityLabel2.SetPosition((int(int((1*3*(self.clockWidth+self.clockMargin))/float(3)))+self.clockX-w/2, int(self.clockHeight / float(4))))
        w,h = dc.GetTextExtent(self.tzDescArray[2])
        self.timeZoneCityLabel3.SetPosition((int(int((2*3*(self.clockWidth+self.clockMargin))/float(3)))+self.clockX-w/2, int(self.clockHeight / float(4))))
        
    def drawCalendar(self):
        ithDay = 1
        jthRow = 0
        monthToDraw = -1
    
        while monthToDraw <= 1:
            if datetime.datetime.today().month + monthToDraw < 1:
                prevMonthDec = datetime.datetime.today().month + monthToDraw + 12
                yearAdj = -1
            else:
                prevMonthDec = 0
                yearAdj = 0
            try:
                thisDate = datetime.datetime(datetime.datetime.today().year + yearAdj, datetime.datetime.today().month + monthToDraw + prevMonthDec, ithDay, 0, 0, 0, 0)
                self.calDate1 = wx.StaticText(self, -1, str(ithDay), pos=(700 + 35*((thisDate.weekday() + 1)%7), 40 + 35*jthRow))
                self.calDate1.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
                if (datetime.datetime(datetime.datetime.today().year + yearAdj, datetime.datetime.today().month + monthToDraw + prevMonthDec, ithDay, 0, 0, 0, 0) == datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 0, 0, 0, 0)):
                    self.calDate1.SetForegroundColour(self.calTodayColor)
                else:
                    if monthToDraw == 0:
                        self.calDate1.SetForegroundColour(self.thisMonthCalDayColor)
                    else:
                        self.calDate1.SetForegroundColour(self.otherMonthCalDayColor)
                ithDay = ithDay + 1
                if thisDate.weekday() == 5:
                    jthRow = jthRow + 1
            except:        
                ithDay = 1
                monthToDraw = monthToDraw + 1

    def clearDrawings(self):
        dc = wx.ClientDC(self)
        dc.Clear()

    def drawLine(self, x1, y1, x2, y2, strokeWidth,  lineColor):
        dc = wx.ClientDC(self)
        dc.SetPen(wx.Pen(lineColor, strokeWidth))
        dc.DrawLine(x1, y1, x2, y2)

    def mouseAway(self, e):
        #WE WANT TO MAKE BACKGROUND TRANSPARENT ON MOUSE AWAY FROM WINDOW, BUT
        #NOT IF THE MOUSE AWAY IS ACTUALLY MOUSE OVER THE WINDOW'S OWN TEXT
        #if self.mouseOver == False:
        self.SetBackgroundColour(self.bgColorMouseAway)
        self.SetTransparent(self.leastOpaqueLevel)
        self.mouseOver = False
        self.drawClocks()
            
    def mouseReturn(self, e):
        #self.SetBackgroundColour(self.bgColorMouseOver)
        self.SetTransparent(self.mostOpaqueLevel)
        self.mouseOver = True
        self.drawClocks()
        

    def mouseMotion(self, e):
        #print str(wx.GetMousePosition())
        if e.LeftIsDown():
            self.Move(wx.Point(wx.GetMousePosition()[0] - self.lastMouseClickPos[0], wx.GetMousePosition()[1] - self.lastMouseClickPos[1]))
        e.Skip()
 
    def leftDown(self, e):
        self.lastMouseClickPos = e.GetPosition()
        e.Skip()

    def toggleTitleBar(self, e):
        if (self.displayTitleBar == True):
            self.style = wx.NO_BORDER
            self.displayTitleBar = False
            self.Show()
            
        elif (self.displayTitleBar == False):
            self.style = wx.SIMPLE_BORDER
            self.displayTitleBar = True
            self.Show()

    def closeWindow(self, e):
        self.changeAlpha_timer.Stop()
        del self.changeAlpha_timer       # avoid a memory leak
        self.Destroy()

    def drawClocks(self, e = None):
        now_utc = datetime.datetime.now(timezone('UTC')) #Put the current time in UTC
        #try:
        self.clearDrawings()
        for i in xrange(3):
            for j in xrange(12):
                self.drawLine(
                int(i*(self.clockWidth + self.clockMargin) + self.clockX + (int(round((self.minuteLength + self.clockTickInnerMargin) * math.cos((math.pi/180)*(((j+1)/float(12)))*360))))),
                int(self.clockHeight + self.clockMargin + int(round((self.minuteLength + self.clockTickInnerMargin) * math.sin((math.pi/180)*(((j+1)/float(12)))*360)))),
                int(i*(self.clockWidth + self.clockMargin) + self.clockX  + (int(round((self.minuteLength + self.clockTickInnerMargin + self.clockTickLength) * math.cos((math.pi/180)*(((j+1)/float(12)))*360))))),
                int(self.clockHeight + self.clockMargin + int(round((self.minuteLength + self.clockTickInnerMargin + self.clockTickLength) * math.sin((math.pi/180)*(((j+1)/float(12)))*360)))), self.tickThick, self.tickColor)

            seconds = float(now_utc.astimezone(timezone(self.tzArray[i])).strftime("%S"))
            minutes = float(now_utc.astimezone(timezone(self.tzArray[i])).strftime("%M"))
            hours = float(now_utc.astimezone(timezone(self.tzArray[i])).strftime("%H"))

            #DRAW CLOCK HANDS
            #LINE(X1,
            #Y1,
            #X2,
            #Y2,
            #THICKNESS, COLOR)
            
            #DRAW HOUR HAND
            self.drawLine(i*(self.clockWidth + self.clockMargin) + self.clockX ,
                          self.clockHeight + self.clockMargin,
                          int(i*(self.clockWidth + self.clockMargin) + self.clockX  + (int(round(self.hourLength * math.cos((math.pi/180)*((((hours-3)%float(12))/float(12))+(minutes/float(60)/12))*360))))),
                          int(self.clockHeight + self.clockMargin + int(round(self.hourLength * math.sin((math.pi/180)*((((hours-3)%float(12))/float(12))+(minutes/float(60)/12))*360)))),
                          self.hourThick, self.hourColor)
            
            #DRAW MINUTE HAND
            self.drawLine(i*(self.clockWidth + self.clockMargin) + self.clockX ,
                          self.clockHeight + self.clockMargin,
                          int(i*(self.clockWidth + self.clockMargin) + self.clockX  + (int(round(self.minuteLength * math.cos((math.pi/180)*((minutes-15)/float(60))*360))))),
                          int(self.clockHeight + self.clockMargin + int(round(self.minuteLength * math.sin((math.pi/180)*((minutes-15)/float(60))*360)))),
                          self.minuteThick, self.minuteColor)

            #DRAW SECOND HAND
            self.drawLine(i*(self.clockWidth + self.clockMargin) + self.clockX ,
                          self.clockHeight + self.clockMargin,
                          int(i*(self.clockWidth + self.clockMargin) + self.clockX  + (int(round(self.secondLength * math.cos((math.pi/180)*((seconds-15)/float(60))*360))))),
                          int(self.clockHeight + self.clockMargin + int(round(self.secondLength * math.sin((math.pi/180)*((seconds-15)/float(60))*360)))),
                          self.secondThick, self.secondColor)
        
if __name__ == '__main__':
    app = wx.App()
    myFrame = Frame(None, 'Organizer', 1000, 800)
    app.MainLoop()
