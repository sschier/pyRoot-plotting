#!/usr/bin/env python

#IMPORTS
import ROOT
from ROOT import RooStats
import sys, copy, os
import argparse, subprocess, commands
import math
from array import array

#GLOBAL VARIABLES
logYAxis = True

#ATLAS STYLE
ROOT.gROOT.LoadMacro("/export/home/prose/myPrograms/scripts/atlasstyle-00-03-05/AtlasUtils.C")
ROOT.gROOT.LoadMacro("/export/home/prose/myPrograms/scripts/atlasstyle-00-03-05/AtlasStyle.C")
ROOT.gROOT.LoadMacro("/export/home/prose/myPrograms/scripts/atlasstyle-00-03-05/AtlasLabels.C")
ROOT.SetAtlasStyle()
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gROOT.ForceStyle()

ROOT.gROOT.SetBatch(True)
#======================================================================
def GetRootFiles(dir, debug):
    file_list = []
    if not dir.endswith("/"): dir = dir + "/"
    files = commands.getoutput('ls ' + dir)
    files = files.split("\n")
    for f in files:
        if f.endswith(".root"): file_list += [dir + f]
    if debug: 
        print dir
        print file_list
    return file_list

#======================================================================
def GetNameFromFileName(file_name_str):

    name = file_name_str.replace('.root', '').split('/')[-1].split('_')[1]
    print name
    return name
#======================================================================
def GetN2MassFromSignalName(signal_name_str):

    mass = signal_name_str.split('-')[1]
    print mass
    return mass
#======================================================================
def GetN1MassFromSignalName(signal_name_str):

    mass = signal_name_str.split('-')[2]
    print mass
    return mass
#======================================================================
def GetHist(root_file_str, hist_path, debug):
    if debug: print 'getting histogram %s' %hist_path
    f = ROOT.TFile(root_file_str, 'READ')
    if debug: print 'file is %s' % f
    h = f.Get(hist_path)
    isTH1 = True
    try: isTH1 = 'TH1' in h.ClassName()
    except: 
        isTH1 = False
    if not isTH1:
        f.Close()
    #    continue
    h.SetDirectory(0)
    hist = copy.deepcopy(h)
    hist.SetDirectory(0)
    f.Close()

    if debug: print hist
    return hist

#======================================================================
def SetRatioCanvas(name, region):
    global logYAxis
    c1 = ROOT.TCanvas("%s_%s" % (name, region), "%s_%s" % (name, region), 0, 0, 800, 600)
    #c1.Divide(1,2,0,0)
    p1 = ROOT.TPad("p1", "p1", 0, 0.5, 1, 1.0)
    p1.SetBottomMargin(0.01)
    if logYAxis: p1.SetLogy(ROOT.kTRUE)
    c1.cd(1)
    p1.Draw()
    primarytextscale=1./(p1.GetWh()*p1.GetAbsHNDC());
    p2 = ROOT.TPad("p2", "p2", 0, 0.0, 1, 0.494)
    p2.SetTopMargin(0.05)
    p2.SetBottomMargin(0.37)
    c1.cd(2)
    p2.Draw()
    ratiotextscale=1./(p2.GetWh()*p2.GetAbsHNDC());

    return c1, p1, p2

#======================================================================
def SetMapCanvas(name, region):

    #Make this canvas for the map
    c1 = ROOT.TCanvas("%s_%s" % (name, region), "%s_%s" % (name, region), 0, 0, 600, 600)
    #c1.Divide(1,2,0,0)
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1.0)
    p1.SetBottomMargin(0)
    if logYAxis: p1.SetLogy(ROOT.kTRUE)
    c1.cd(1)
    p1.Draw()
    p2 = ROOT.TPad("p2", "p2", 0, 0.0, 1, 0.3)
    p2.SetTopMargin(0)
    p2.SetBottomMargin(0.3)
    c1.cd(2)
    p2.Draw()

    return c1, p1, p2

#======================================================================
def Make1Legend(base, trig, N2, N1, name):

    #sortedHistTuple = sorted(bkgndHists, key=lambda x: x.GetBinContent(x.GetMaximumBin()))
    #sortedHistTuple = sorted(bkgndHists.items(), key=lambda x: x[1].GetBinContent(x[1].GetMaximumBin()), reverse=True)

    l = ROOT.TLegend(0.6, 0.8, 0.91, 0.95)
    #Call a function that gets the mass points to put in the legend
    l.AddEntry(base, 'm(#tilde{#Chi}_{2}^{0},#tilde{#Chi}_{1}^{0}) (%s, %s) GeV' % (N2, N1), 'l')
    l.AddEntry(trig, name, 'l') 

    return l

#======================================================================
def MakeLegend(base, trig1, trig2, trig3, trig4, N2, N1):

    #sortedHistTuple = sorted(bkgndHists, key=lambda x: x.GetBinContent(x.GetMaximumBin()))
    #sortedHistTuple = sorted(bkgndHists.items(), key=lambda x: x[1].GetBinContent(x[1].GetMaximumBin()), reverse=True)

    l = ROOT.TLegend(0.6, 0.8, 0.91, 0.95)
    #Call a function that gets the mass points to put in the legend
    l.AddEntry(base, 'm(#tilde{#Chi}_{2}^{0},#tilde{#Chi}_{1}^{0}) (%s, %s) GeV' % (N2, N1), 'l')
    l.AddEntry(trig1, 'HLT_mu4_j125_xe90_mht', 'l') 
    l.AddEntry(trig2, 'HLT_2mu4_j85_xe50_mht', 'l') 
    l.AddEntry(trig3, 'Inclusive Met Trigger', 'l') 
    l.AddEntry(trig4, 'OR Of All 3 Triggers', 'l') 



    #for hist in sortedHistTuple:
    #    l.AddEntry(hist[1], hist[0], 'f')
    #for hist, name in zip(sortedHistTuple, samples):
    #    l.AddEntry(hist, name, 'f')

    return l

#======================================================================
def MakeEff(topHist, bottomHist):

    rh = copy.deepcopy(topHist)
    rh.SetDirectory(0)
    rh.Divide(bottomHist)
    rh.SetMinimum(0)
    rh.SetMaximum(1.2)
    print '*****'
    print topHist.GetXaxis().GetTitle()
    rh.GetXaxis().SetTitle(str(topHist.GetXaxis().GetTitle()))
    #if bottomHist == 'lep_type':
    #    rh.GetXaxis().SetBinLabel(2,(str(bottomHist.GetXaxis().GetBinLabel(2))))
    #    rh.GetXaxis().SetBinLabel(3,(str(bottomHist.GetXaxis().GetBinLabel(3))))
    rh.GetXaxis().SetLabelSize(0.1)
    rh.GetYaxis().SetLabelSize(0.1)
    rh.GetYaxis().SetNdivisions(6)
    rh.GetXaxis().SetTitleSize(0.1)
    rh.GetYaxis().SetTitleSize(0.1)
    rh.GetXaxis().SetTitleOffset(0.9)
    rh.GetYaxis().SetTitleOffset(0.41)
    rh.GetYaxis().SetTitle("Trigger Eff")

    #zeroline=rh.TLine(0, 1.0, xmax, 1.0)
    #zeroline.SetLineWidth(2)
    #zeroline.Draw()

    return rh
#======================================================================
def plot1(num_path, denom_path, region, infile, var, lepPair, color, name, debug):
    if debug: print "opening output file"
    o=ROOT.TFile("test.root", "RECREATE")

    N1          = GetN1MassFromSignalName(GetNameFromFileName(infile))
    N2          = GetN2MassFromSignalName(GetNameFromFileName(infile))
    m_denom     = GetHist(infile, denom_path, debug)
    m_num       = GetHist(infile, num_path, debug)
    m_eff       = MakeEff(m_num, m_denom)
    #print "Making legend"
    m_legend = Make1Legend(m_denom, m_num, N2, N1, name)
    #maxVal = m_denom.GetBinContent(m_denom.GetMaximumBin())*10
    maxVal = 100000


    m_denom.GetYaxis().SetLabelSize(0.1)
    m_denom.GetYaxis().SetTitle("")
    m_denom.SetLineColor(2)
    m_denom.SetLineStyle(5)
    m_denom.Scale(9600)
    m_denom.SetMaximum(maxVal)
    m_num.SetLineColor(color)
    m_num.SetMarkerSize(0)
    m_num.Scale(9600)
    print "Making canvas and drawing"
    canvas, p1, p2 = SetRatioCanvas('canvas', region)
    p2.cd()
    m_eff.SetMarkerSize(0.1)
    m_eff.SetLineColor(color)
    m_eff.Draw("P")
    p1.cd()
    m_denom.Draw("HIST")
    m_num.Draw("HSAME")
    o.cd()
    canvas.Write()

    canvas.cd()
    m_legend.Draw()
    ROOT.gStyle.SetLegendBorderSize(0)
    ROOT.gROOT.ForceStyle()
    ROOT.myText(       0.21,  0.85, 1, "9.6fb^{-1}@ #sqrt{s}= 13 TeV")
    #ROOT.myText(       0.41,  0.80, 1, "data16PeriodK")
    #ROOT.myText(       0.41,  0.85, 1, "%s" % region)
    ROOT.ATLASLabel(0.21,0.90,"Internal")
    #raw_input("-->")
    canvas.Print('eff_%s_%s_%s_%s.pdf' % (lepPair, region, N2, N1))
    return True
#======================================================================
def plotAll(num1_path, num2_path, num3_path, num4_path, denom_path, region, infile, var, lepPair, debug):
    if debug: print "opening output file"
    o=ROOT.TFile("test.root", "RECREATE")
    mass_point = GetNameFromFileName(infile)
    N1 = GetN1MassFromSignalName(mass_point)
    N2 = GetN2MassFromSignalName(mass_point)
    m_denom = GetHist(infile, denom_path, debug)
    m_num1  = GetHist(infile, num1_path, debug)
    m_num2  = GetHist(infile, num2_path, debug)
    m_num3  = GetHist(infile, num3_path, debug)
    m_num4  = GetHist(infile, num4_path, debug)
    m_eff1 = MakeEff(m_num1, m_denom)
    m_eff2 = MakeEff(m_num2, m_denom)
    m_eff3 = MakeEff(m_num3, m_denom)
    m_eff4 = MakeEff(m_num4, m_denom)
    print "Making legend"
    m_legend = MakeLegend(m_denom, m_num1, m_num2, m_num3, m_num4, N2, N1)
    #maxVal = m_denom.GetBinContent(m_denom.GetMaximumBin())*10
    maxVal = 100000


    m_denom.GetYaxis().SetLabelSize(0.1)
    m_denom.GetYaxis().SetTitle("")
    m_denom.SetLineColor(2)
    m_denom.SetLineStyle(5)
    m_denom.Scale(9600)
    m_denom.SetMaximum(maxVal)
    m_num1.SetLineColor(30)
    m_num1.SetMarkerSize(0)
    m_num1.Scale(9600)
    m_num2.SetLineColor(47)
    m_num2.SetMarkerSize(0)
    m_num2.Scale(9600)
    m_num3.SetLineColor(50)
    m_num3.SetMarkerSize(0)
    m_num3.Scale(9600)
    m_num4.SetLineColor(7)
    m_num4.SetMarkerSize(0)
    m_num4.Scale(9600)
    print "Making canvas and drawing"
    canvas, p1, p2 = SetRatioCanvas('canvas', region)
    p2.cd()
    m_eff1.SetMarkerSize(0.1)
    m_eff1.SetLineColor(30)
    m_eff1.Draw("P")
    m_eff2.SetMarkerSize(0.1)
    m_eff2.SetLineColor(47)
    m_eff2.Draw("PSAME")
    m_eff3.SetMarkerSize(0.1)
    m_eff3.SetLineColor(50)
    m_eff3.Draw("PSAME")
    m_eff4.SetMarkerSize(0.1)
    m_eff4.SetLineColor(7)
    m_eff4.Draw("PSAME")
    p1.cd()
    m_denom.Draw("HIST")
    m_num1.Draw("HSAME")
    m_num2.Draw("HSAME")
    m_num3.Draw("HSAME")
    m_num4.Draw("HSAME")
    o.cd()
    canvas.Write()

    canvas.cd()
    m_legend.Draw()
    ROOT.gStyle.SetLegendBorderSize(0)
    ROOT.gROOT.ForceStyle()
    ROOT.myText(       0.21,  0.85, 1, "9.6fb^{-1}@ #sqrt{s}= 13 TeV")
    #ROOT.myText(       0.41,  0.80, 1, "data16PeriodK")
    #ROOT.myText(       0.41,  0.85, 1, "%s" % region)
    ROOT.ATLASLabel(0.21,0.90,"Internal")
    #raw_input("-->")
    canvas.Print('eff_%s_%s_%s_%s.pdf' % (lepPair, region, N2, N1))
    return True
#======================================================================
def main(argv):

    parser = argparse.ArgumentParser(description="Command line arguments")
    parser.add_argument("-vars"          , action='store', default='')
    parser.add_argument("-indir"        , action='store', default='')
    parser.add_argument("-outfile"      , action='store', default='')
    parser.add_argument("--test"        , action='store_true')
    parser.add_argument("-region"       , action='store', default="SR")
    args=parser.parse_args()

    print "Congratulations!"

    file_list = GetRootFiles(args.indir, args.test)
    denom1mu_path = 'EWsignalMM/EWsignalMM_jet145/h_EWsignalMM_jet145_MET'
    denom2mu_path = 'EWsignalMM/EWsignalMM_jet105/h_EWsignalMM_jet105_MET'
    numer1mu_path = 'EWsignal1muTrigMM/EWsignal1muTrigMM_mtautau/h_EWsignal1muTrigMM_mtautau_MET'
    numer2mu_path = 'EWsignal2muTrigMM/EWsignal2muTrigMM_mtautau/h_EWsignal2muTrigMM_mtautau_MET'
    denom_path = []
    mu1T_path  = []
    mu2T_path  = []
    metT_path  = []
    ORtT_path  = []
    #cut_list = ['skim', 'opSign', 'ratio_MET_Had', 'Ht', 'ptll', 'mll', 'lepPt', 'bVeto', 'mtLepMET', 'mtautau']
    #pair_list = ['EE', 'MM', 'EM']
    #pair_list = ['MM', 'EM']
    pair_list = ['MM']
    cut_list = ['skim', 'signal', 'opSign', 'mtautau'] #'jet105' and 'jet145'
    for p  in pair_list:
        denom_path = []
        mu1T_path  = []
        mu2T_path  = []
        metT_path  = []
        for c in cut_list:
            denom_path += ['EWsignal%s/EWsignal%s_%s/h_EWsignal%s_%s_MET' % (p, p, c, p, c)]
            mu1T_path  += ['EWsignal1muTrig%s/EWsignal1muTrig%s_%s/h_EWsignal1muTrig%s_%s_MET' % (p, p, c, p, c)]
            mu2T_path  += ['EWsignal2muTrig%s/EWsignal2muTrig%s_%s/h_EWsignal2muTrig%s_%s_MET' % (p, p, c, p, c)]
            metT_path  += ['EWsignalMetTrig%s/EWsignalMetTrig%s_%s/h_EWsignalMetTrig%s_%s_MET' % (p, p, c, p, c)]
            ORtT_path  += ['EWsignalORTrig%s/EWsignalORTrig%s_%s/h_EWsignalORTrig%s_%s_MET'    % (p, p, c, p, c)]
    #denom_path = 'EWsignal/EWsignal_skim/h_EWsignal_skim_MET'
    #num1_path  = 'EWsignal1muTrig/EWsignal1muTrig_skim/h_EWsignal1muTrig_skim_MET'
    #num2_path  = 'EWsignal2muTrig/EWsignal2muTrig_skim/h_EWsignal2muTrig_skim_MET'

        #print p
        #`print denom_path

        for string in file_list:
            for d, h1, h2, h3, h4, c in zip(denom_path, mu1T_path, mu2T_path, metT_path, ORtT_path, cut_list):
                plotAll(h1, h2, h3, h4, d, c, string, 'MET', p, args.test)
            plot1(numer1mu_path, denom1mu_path, 'jet145', string, 'MET', p, 30, 'HLT_mu4_j125_xe90_mht',  args.test)
            plot1(numer2mu_path, denom2mu_path, 'jet105', string, 'MET', p, 47, 'HLT_2mu4_j85_xe50_mht',  args.test)

    #xbins = [80., 100., 150., 200., 250., 300., 400.]
    #ybins = [83., 85., 90., 100., 103.,  105., 110., 120., 140., 150., 155., 160., 170., 180., 190., 200., 205., 210., 220., 240., 250., 255., 260., 270., 290., 300., 305., 310., 320., 340., 350., 360., 400., 405., 410., 420., 440., 460., 500.]
    #h_HLT_2mu4 = ROOT.TH2F("h_HLT_2mu4", "h_HLT_2mu4", 6, array('d',xbins), 30, array('d',ybins))
    ##h_HLT_2mu4 = ROOT.TH2F("h_HLT_2mu4", "h_HLT_2mu4", 7, 80., 101., 30, 83., 500. )
    #h_HLT_2mu4.Draw("colz")
    #raw_input("--->")
    #print xbins[0]
    if args.test:
        print "Done"



if __name__ == '__main__':
    main(sys.argv[1:])
 #======================================================================
