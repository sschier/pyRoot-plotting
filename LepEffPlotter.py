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
ROOT.gROOT.LoadMacro("/export/home/sschier/workarea/atlasstyle-00-03-05/AtlasUtils.C")
ROOT.gROOT.LoadMacro("/export/home/sschier/workarea/atlasstyle-00-03-05/AtlasStyle.C")
ROOT.gROOT.LoadMacro("/export/home/sschier/workarea/atlasstyle-00-03-05/AtlasLabels.C")
ROOT.SetAtlasStyle()
ROOT.gStyle.SetLegendBorderSize(0)
ROOT.gROOT.ForceStyle()
ROOT.gROOT.SetBatch(True)

truth_name = 'outputHistTruth'
reco_name = 'outputHist'
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
def isTruth(file_name):
    isTruth = False
    name = file_name.replace('.root', '').split('/')[-1].split('_')[0]
    print name
    if name == truth_name:
        isTruth = True
    return isTruth
#======================================================================
def isReco(file_name):
    isReco = False
    name = file_name.replace('.root', '').split('/')[-1].split('_')[0]
    print name
    if name == reco_name:
        isReco = True
    print 'is Reco? %s' % isReco
    return isReco
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
def GetRecoHist(file_list, hist_path, debug):
    if debug: print 'getting reco hist'
    recoHist = ROOT.TH1F()
    for string in file_list:
        if isReco(string):
            f = ROOT.TFile(string, 'READ')
            if debug: print "reco file is: %s" % f
            h = f.Get(hist_path)
            print h.ClassName()
            h.SetDirectory(0)
            recoHist = copy.deepcopy(h)
            recoHist.SetDirectory(0)
    print recoHist
    return recoHist
#======================================================================
def GetTruthHist(file_list, hist_path, debug):
    if debug: print 'getting truth hist'
    truthHist = ROOT.TH1F()
    for string in file_list:
        if isTruth(string):
            f = ROOT.TFile(string, 'READ')
            if debug: print "truth file is: %s" % f
            h = f.Get(hist_path)
            print h.ClassName()
            h.SetDirectory(0)
            truthHist = copy.deepcopy(h)
            truthHist.SetDirectory(0)
    print truthHist
    return truthHist
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
def MakeLegend(h_denom, t_denom, l_denom, h_num, t_num, l_num):

    #sortedHistTuple = sorted(bkgndHists, key=lambda x: x.GetBinContent(x.GetMaximumBin()))
    #sortedHistTuple = sorted(bkgndHists.items(), key=lambda x: x[1].GetBinContent(x[1].GetMaximumBin()), reverse=True)

    l = ROOT.TLegend(0.6, 0.8, 0.91, 0.95)
    #Call a function that gets the mass points to put in the legend
    l.AddEntry(h_denom, '%s_%s' % (t_denom, l_denom), 'l')
    l.AddEntry(h_num, '%s_%s' % (t_num, l_num), 'l') 

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
def plot1(num_path, num_type, num_lep, denom_path, denom_type, denom_lep, var, lepPair, indir, debug):
    if debug: print "opening output file"
    o=ROOT.TFile("test.root", "RECREATE")

    file_list = GetRootFiles(indir, 1)
    infile = file_list[0]
    N1          = GetN1MassFromSignalName(GetNameFromFileName(infile))
    N2          = GetN2MassFromSignalName(GetNameFromFileName(infile))
    if denom_type == 'truth':
        m_denom   = GetTruthHist(file_list, denom_path, 1)
    elif denom_type == 'reco':
        m_denom   = GetRecoHist(file_list, denom_path, 1)
    else: print "Please specify denominator type"
    if num_type == 'truth':
        m_num     = GetTruthHist(file_list, num_path, debug)
    elif num_type == 'reco':
        m_num     = GetRecoHist(file_list, num_path, debug)
    else: print "Please specify numerator type"
    m_eff       = MakeEff(m_num, m_denom)
    #print "Making legend"
    m_legend = MakeLegend(m_denom, denom_type, denom_lep, m_num, num_type, num_lep)
    #maxVal = m_denom.GetBinContent(m_denom.GetMaximumBin())*10
    maxVal = 1000


    m_denom.GetYaxis().SetLabelSize(0.1)
    m_denom.GetYaxis().SetTitle("")
    m_denom.SetLineColor(2)
    m_denom.SetLineStyle(5)
    m_denom.Scale(9600)
    m_denom.SetMaximum(maxVal)
    m_num.SetLineColor(43)
    m_num.SetMarkerSize(0)
    m_num.Scale(9600)
    print "Making canvas and drawing"
    canvas, p1, p2 = SetRatioCanvas('canvas', var)
    p2.cd()
    m_eff.SetMarkerSize(0.1)
    m_eff.SetLineColor(43)
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
    ROOT.myText(       0.21,  0.80, 1, 'm(#tilde{#Chi}_{2}^{0},#tilde{#Chi}_{1}^{0}) (%s, %s) GeV' % (N2, N1))
    #ROOT.myText(       0.41,  0.85, 1, "%s" % region)
    ROOT.ATLASLabel(0.21,0.90,"Internal")
    #raw_input("-->")
    canvas.Print('eff_%s_%s_%s_%s_%s%sOVER%s%s.pdf' % (lepPair, var, N2, N1, num_type, num_lep, denom_type, denom_lep))
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
    hist_recoBase = ROOT.TH1F()
    hist_recoSignal = ROOT.TH1F()
    hist_truthBase = ROOT.TH1F()
    hist_truthSignal = ROOT.TH1F()
    #base_path = 'baseLeptonsMM/baseLeptonsMM_skim/h_baseLeptonsMM_skim_Rll'
    #signal_path = 'signalLeptonsMM/signalLeptonsMM_skim/h_signalLeptonsMM_skim_Rll'
    pair_list = ['EE', 'MM', 'EM']
    var_list = ['Rll', 'Ptll', 'Mll']
    for p in pair_list:
        base_path_list = []
        signal_path_list = []
        for v in var_list:
            base_path_list    += ['baseLeptons%s/baseLeptons%s_skim/h_baseLeptons%s_skim_%s' % (p, p, p, v)]
            signal_path_list  += ['signalLeptons%s/signalLeptons%s_skim/h_signalLeptons%s_skim_%s' % (p, p, p, v)]
        for s, b, v in zip(signal_path_list, base_path_list, var_list):
            plot1(s, 'reco', 'signalLep', b, 'reco', 'baseLep', v, p, args.indir,  args.test)
            plot1(b, 'reco', 'baseLep', b, 'truth', 'baseLep', v, p, args.indir,  args.test)
            plot1(s, 'reco', 'signalLep', s, 'truth', 'signalLep', v, p, args.indir,  args.test)
            plot1(s, 'truth', 'signalLep', b, 'truth', 'baseLep', v, p, args.indir,  args.test)

    if args.test:
        print "Done"



if __name__ == '__main__':
    main(sys.argv[1:])
 #======================================================================
