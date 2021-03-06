import numpy as np
import scipy as sp
import scipy.signal
import scipy.linalg
import matplotlib.pyplot as plt

class dsp:
    @staticmethod
    def autocorrelation(signal):
        '''
        The unbiased cross-correlation of a signal with itself
        '''
        autocorrelation = [np.mean(signal * np.roll(signal, shift))
                           for shift in range(signal.size)]

        variance = autocorrelation[0]
        print(f'Signal Variance: {variance}, {np.var(signal)}')
        return autocorrelation

    @staticmethod
    def powerspectrum(signal):
        return np.fft.fft(dsp.autocorrelation(signal))

def pisarenko(signal, order, autocorrelation=None):
    '''
    Pisarenko's method for frequency estimation
    Process is assumed to consist of order complex exponentials in white noise

    signal: signal with additive white noise

    TODO:
        - use covariance
        - handle 0-meaning iput data, or just calculate the covariance
    '''
    if autocorrelation is None:
        # estimate the (order + 1) x (order + 1) autocorrelation matrix
        autocorrelation = dsp.autocorrelation(signal)

    # autocorrelation sequence MUST be of size > order + 1
    # only the first (order + 1) of the autocorrelation sequence is used
    rx = np.array(autocorrelation[:order + 1])

    # (order + 1) x (order + 1) hermitian toeplitz auttocorrelation matrix
    autocorrelation_matrix = scipy.linalg.toeplitz(rx)
    print(autocorrelation_matrix)

    # since autocorrelation matrix is hermitian toeplitz, eigenvalues are non-negative real
    eval, evec = np.linalg.eigh(autocorrelation_matrix)
    print(f'Eigenvalues: {eval}')
    print("Eigenvectors: ", evec)

    # there is only one noise vector
    # it is the column vector corresponding to the minimum eigenvalue
    # the minimum eigenvalue absolute value is the variance of the additive white noise
    vmin_i = np.argmin(eval)
    variance = eval[vmin_i]
    print(f'Min eigenval (variance of white noise): {variance}')
    # noise vector
    vmin = evec[:,vmin_i]
    eigenfilter = scipy.signal.tf2zpk([1], vmin)
    print("Eigenfilter: ", eigenfilter)

    # estimated frequencies
    freqs = np.arccos(np.angle(eigenfilter[1]) / 2)

    # there are (order) signal vectors
    # TODO: calculate power associat ed with each signal vector

    return freqs, variance

if __name__ == "__main__":
    SAMPLE_COUNT = 1024
    space = np.linspace(0, 10*2*np.pi, SAMPLE_COUNT)
    var = 0.01
    noise = np.random.normal(0, np.sqrt(var), SAMPLE_COUNT)
    sig = np.sin(space) + noise
    mean = np.mean(sig)
    print(f'Process Mean: {mean}')
    # zero-mean the process
    sig -= mean

    ac = np.array([6, 1.92705 + 4.58522j, -3.42705 + 3.49541j])
    freqs, variance = pisarenko(sig, 2)

    print(f'Frequencies: {freqs}')
    print(f'Variance: {variance}')
    #ps = dsp.powerspectrum(sig)
    #peaks, _ = scipy.signal.find_peaks(sig)
    #if len(peaks):
        #print(sig[peaks])

    plt.figure(0)
    plt.plot(space, sig)
    #plt.figure(1)
    #plt.plot(ps)
    plt.grid()
    plt.show()
