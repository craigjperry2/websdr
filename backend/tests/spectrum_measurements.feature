Feature: Estimate spectral density and broadcast to clients via websocket

  Use a Software Defined Radio connected to the host machine to measure a
  portion of the radio spectrum. Calculate spectral density estimates from
  the observed measurements using Welch's method and broadcast the results
  in JSON format to all connected websocket clients. Results can then be
  used to measure, analyse and present the observed radio spectrum.

  Scenario Outline: Stream Welch's method spectral density estimates
    
    Power measurements are given in an array of frequency bins. The bins
    are of width rbw and are ordered Flo -> Fhi.

    Given the SDR dongle is ready
      And the websocket server is ready
     When 2 clients connect via websocket to "/iqstream"
     Then they receive identical streams of json map objects
      And the maps have <key> of <type> with values between <min> and <max>

    Examples:
      | key      | type      | min  | max  | description                      |
      | Flo      | int       | 1    | 2000 | Low edge frequency (MHz)         |
      | Fhi      | int       | 1    | 2000 | High edge frequency (MHz)        |
      | rbw      | int       | 500  | 2000 | Resolution bandwidth (Hz)        |
      | Pxx      | List[int] | 512  | 2048 | List of power spectral densities |
      | Pxx[0]   | int       | -150 | 0    | Power measurements (V^2/Hz)      |
      | Pxx[123] | int       | -150 | 0    | Power measurements (V^2/Hz)      |
      | Pxx[456] | int       | -150 | 0    | Power measurements (V^2/Hz)      |
      | Pxx[511] | int       | -150 | 0    | Power measurements (V^2/Hz)      |
