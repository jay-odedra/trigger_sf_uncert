import ROOT
import numpy as np
import random
import CMS_lumi, tdrstyle
ROOT.gStyle.SetStatY(0.9)
ROOT.gStyle.SetStatX(0.9) 
br_rare = 0.00000056
br_jpsi = 0.0000602316
ratioBR = br_rare / br_jpsi
lowqtoy = 485232391
jpsitoy = 506005157
Lumi = 33.85
bb_cross_section = 4.70E+11
fragmentation_fraction = 0.4

jpsidata = 63000
mean_list = []
sigma_list = []
mcjpsi_total = []
mclowq_total = []
mchighq_total = []

for i in range(100):
    mclowq = np.loadtxt(f'/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors_04_03_25/Step_3_integral_calc/integral_rare/integrals_rare_100_part_{i}_.txt')
    mcjpsi = np.loadtxt(f'/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors_04_03_25/Step_3_integral_calc/integral_jpsi/integrals_jpsi_100_part_{i}_.txt')
    #mchighq = np.loadtxt(f'/eos/user/j/jodedra/AnalysisWork_2024/systematics/TriggerScaleFactors/MakingScaleFactorTuples/ScaleFactors/rarevaluessampler/High_q_region/integrals_rare_100_part_{i}_.txt')
    mcjpsi_total.extend(mcjpsi)
    mclowq_total.extend(mclowq)
    #mchighq_total.extend(mchighq)
print("mcjpsi_mean: ", np.mean(mcjpsi_total))
print("mclowq_mean: ", np.mean(mclowq_total))
#print("mchighq_mean: ", np.mean(mchighq))
print("mcjpsi_std: ", np.std(mcjpsi_total))
print("mclowq_std: ", np.std(mclowq_total))
#print("mchighq_std: ", np.std(mchighq))

hundred_mcjpsi_total = []
hundred_mclowq_total = []
#hundred_mchighq = []
for i in range(1):
    #random.shuffle(mclowq_total)
    #random.shuffle(mcjpsi_total)
    hundred_mcjpsi_total.extend(mcjpsi_total)
    hundred_mclowq_total.extend(mclowq_total)
#    hundred_mchighq.extend(mchighq_total)

predlowqlist = [jpsidata * ((x/lowqtoy) / (y/jpsitoy)) * ratioBR for x, y in zip(hundred_mclowq_total, hundred_mcjpsi_total)]
#predhighqlist = [jpsidata * (x / y) * ratioBR for x, y in zip(hundred_mchighq, hundred_mcjpsi_total)]
output_file = ROOT.TFile("gaussian_fit_histograms.root", "RECREATE")

hist = ROOT.TH1F(f"Gaussian fit param", "", 100, min(predlowqlist), max(predlowqlist))
hist.GetXaxis().SetTitle("Predicted low-q^{2} Normalisation")


hist_jpsi = ROOT.TH1F(f"Gaussian fit param", "", 100, min(hundred_mcjpsi_total), max(hundred_mcjpsi_total))
hist_jpsi.GetXaxis().SetTitle("MC J/#psi")


hist_lowq = ROOT.TH1F(f"Gaussian fit param", "", 100, min(hundred_mclowq_total), max(hundred_mclowq_total))
hist_lowq.GetXaxis().SetTitle("MC low-q^{2}")

#hist2 = ROOT.TH1F(f"Gaussian fit param", "Trigger Scale Factor Stat uncertainty sampling", 100, min(predhighqlist), max(predhighqlist))
#hist2.GetXaxis().SetTitle("Predicted high-q^{2} Normalisation")

# Fill the histogram with data
#for value in predlowqlist:
#    hist.Fill(value)
for i in range(len(predlowqlist)):
    hist.Fill(predlowqlist[i])
    hist_jpsi.Fill(hundred_mcjpsi_total[i])
    hist_lowq.Fill(hundred_mclowq_total[i])
    
#for value in predhighqlist:
#    hist2.Fill(value)
ROOT.gStyle.SetOptFit(111)
ROOT.gStyle.SetStatW(0.15)  # Width of the stat box
ROOT.gStyle.SetStatH(0.1) 
# Fit the histogram with a Gaussian
gaussian = ROOT.TF1("gaussian", "gaus", min(predlowqlist), max(predlowqlist))
hist.Fit(gaussian, "R")
mean = gaussian.GetParameter(1)
sigma = gaussian.GetParameter(2)
#mean_list.append(mean)
#sigma_list.append(sigma)
ROOT.gStyle.SetOptFit(111)

#gaussian2 = ROOT.TF1("gaussian2", "gaus", min(predhighqlist), max(predhighqlist))
#hist2.Fit(gaussian2, "R")
#mean2 = gaussian2.GetParameter(1)
#sigma2 = gaussian2.GetParameter(2)
#ROOT.gStyle.SetOptFit(111)

gaussian2 = ROOT.TF1("gaussian2", "gaus", min(hundred_mcjpsi_total), max(hundred_mcjpsi_total))
hist_jpsi.Fit(gaussian2, "R")
mean2 = gaussian2.GetParameter(1)
sigma2 = gaussian2.GetParameter(2)
ROOT.gStyle.SetOptFit(111)


gaussian3 = ROOT.TF1("gaussian3", "gaus", min(hundred_mclowq_total), max(hundred_mclowq_total))
hist_lowq.Fit(gaussian3, "R")
mean3 = gaussian3.GetParameter(1)
sigma3 = gaussian3.GetParameter(2)
ROOT.gStyle.SetOptFit(111)

# Create a ROOT file to save the histograms
#output_file = ROOT.TFile("gaussian_fit_histograms.root", "RECREATE")
'''
for i in range(1):
    random.shuffle(mclowq_total)
    random.shuffle(mcjpsi_total)
    predlowqlist = [jpsidata * (x / y) * ratioBR for x, y in zip(mclowq_total, mcjpsi_total)]
    
    # Create a histogram
    hist = ROOT.TH1F(f"hist_{i}", "Trigger Scale Factor Stat uncertainty sampling", 200, min(predlowqlist), max(predlowqlist))
    hist.GetXaxis().SetTitle("Predicted low-q^{2} Normalisation")
    
    # Fill the histogram with data
    for value in predlowqlist:
        hist.Fill(value)

    # Fit the histogram with a Gaussian
    gaussian = ROOT.TF1("gaussian", "gaus", min(predlowqlist), max(predlowqlist))
    hist.Fit(gaussian, "R")
    mean = gaussian.GetParameter(1)
    sigma = gaussian.GetParameter(2)
    mean_list.append(mean)
    sigma_list.append(sigma)
    ROOT.gStyle.SetOptFit(111)
    # Write the histogram to the ROOT file
'''


#meanofmeans = np.mean(mean_list)
#sigmaofmeans = np.mean(sigma_list)

#print("Mean of means: ", meanofmeans)
#print("Mean of sigmas: ", sigmaofmeans)

# Close the ROOT file

# Draw the last histogram and the fit
canvas = ROOT.TCanvas("canvas", "canvas", 1600, 1200)

ROOT.gStyle.SetStatW(0.00015)  # Width of the stat box
ROOT.gStyle.SetStatH(0.0001)
ROOT.gStyle.SetOptFit(111)
hist.GetYaxis().SetTitle("N Events")
hist.Draw()
gaussian.Draw("same")
CMS_lumi.CMS_lumi(canvas, 1, 10)
canvas.SaveAs("gaussian_fit_stat_uncertainty_tester.png")
canvas.SaveAs("gaussian_fit_stat_uncertainty_tester.pdf")

# Optionally, show the plot
hist.Write()
canvas.Delete()
#canvas2 = ROOT.TCanvas("canvas", "canvas", 1600, 1200)
#ROOT.gStyle.SetStatW(0.00015)  # Width of the stat box
#ROOT.gStyle.SetStatH(0.0001)
#hist2.Draw()
#gaussian2.Draw("same")
#canvas2.SaveAs("gaussian_fit_stat_uncertainty_tester_highq.png")
#canvas2.SaveAs("gaussian_fit_stat_uncertainty_tester_highq.pdf")
#canvas2.Draw()
#hist2.Write()
canvas2 = ROOT.TCanvas("canvas2", "canvas2", 1600, 1200)

ROOT.gStyle.SetStatW(0.00015)  # Width of the stat box
ROOT.gStyle.SetStatH(0.0001)
ROOT.gStyle.SetOptFit(111)
hist_jpsi.GetYaxis().SetTitle("N Events")

hist_jpsi.Draw()
gaussian2.Draw("same")
CMS_lumi.CMS_lumi(canvas2, 1, 10)
canvas2.SaveAs("gaussian_fit_jpsi.png")
canvas2.SaveAs("gaussian_fit_jpsi.pdf")

# Optionally, show the plot
hist_jpsi.Write()
canvas2.Delete()




canvas3 = ROOT.TCanvas("canvas3", "canvas3", 1600, 1200)

ROOT.gStyle.SetStatW(0.00015)  # Width of the stat box
ROOT.gStyle.SetStatH(0.0001)
ROOT.gStyle.SetOptFit(111)
hist_lowq.GetYaxis().SetTitle("N Events")
hist_lowq.Draw()
gaussian3.Draw("same")

CMS_lumi.CMS_lumi(canvas3, 1, 10)
canvas3.SaveAs("gaussian_fit_lowq.png")
canvas3.SaveAs("gaussian_fit_lowq.pdf")

# Optionally, show the plot
hist_lowq.Write()
canvas3.Delete()

output_file.Close()
