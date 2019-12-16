import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as st
import pandas as pd


class simulator:
    def __init__(self, population, effect, alpha, n):
        self.population = population
        self.effect = effect
        self.alpha = alpha
        self.n = n
        self.mu = self.population.mean()
        self.sigma = self.population.std()
        self.xbase = np.random.choice(self.population, size=self.n)
        self.xvar = np.random.choice(self.population, size=self.n) + self.effect
        self.t = st.ttest_rel(self.xvar, self.xbase)


    def ci(self, sample, alpha = 0.05):
        sample_mean_ = np.mean(sample)
        sample_std_ = np.std(sample)
        n = len(sample)
        z_confidence_level = st.norm.ppf((1-self.alpha))

        CI_low = sample_mean_ - z_confidence_level*(sample_std_/np.sqrt(n))
        CI_high = sample_mean_ + z_confidence_level*(sample_std_/np.sqrt(n))
        return CI_low, sample_mean_, CI_high



    def ciPlot(self, **kwargs):
        """
        base={'name': 'base', 'color': 'green'}
        , variant={'name': 'variant', 'color': 'blue'}

	"""
        variant = kwargs['variant']
        base = kwargs['base']

        for x_n in [(self.xvar, variant['name'], variant['color']), (self.xbase, base['name'], base['color'])]:

            CI_low, sample_mean_, CI_high = self.ci(sample=x_n[0], alpha=self.alpha)
            x_err = CI_high - CI_low
            name = x_n[1]
            color = x_n[2]
            plt.errorbar(sample_mean_, np.array([name]), xerr=x_err, fmt='o', color=color,
                         ecolor=color, elinewidth=5, capsize=25)

        plt.xlim(left=0)
        plt.xlim(right=self.mu + self.effect + 2*self.sigma)
        plt.axvline(x=self.mu, linestyle='--', color=base['color'])
        plt.axvline(x=self.mu+self.effect, linestyle='--', color=variant['color'])
        plt.show()

    def ttestPlot(self):
        """
        The Standard Normal Distribution Plot
        with the observed t-stat
        """
        r = np.arange(-4,4,0.001)
        plt.plot(r, st.norm.pdf(r, 0, 1))
        plt.axvline(x=2, ymax=0.2,color='k')
        plt.axvline(x=-2, ymax=0.2,color='k')
        plt.plot(self.t.statistic, 0, marker='x', markersize=8,)
        plt.show()


    def table(self):
        df = pd.DataFrame({'base': [0, self.xbase.mean(), self.xbase.std(), self.n]
                        , 'variant': [self.effect, self.xvar.mean(), self.xvar.std(), self.n]}
                        , index=['effect', 'mean', 'std', 'n'])
        return round(df, 3)




