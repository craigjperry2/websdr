Feature: Estimate spectral density and broadcast to clients via websocket

  Use a Software Defined Radio connected to the host machine to measure a
  portion of the radio spectrum. Calculate spectral density estimates from
  the observed measurements using Welch's method and broadcast the results
  in JSON format to all connected websocket clients. Results can then be
  used to measure, analyse and present the observed radio spectrum.

  Scenario Outline: Stream Welch's method spectral density estimates

    Given the SDR dongle is ready
    And the websocket server is ready
    When 2 clients connect via websocket to sde
    Then they receive identical streams of json map objects
    And the maps have <key> of <dtype> with values between <min> and <max>

    Examples:
      | key      | dtype          | min  | max  |
      | f        | <class 'list'> | 512  | 2048 |
    # | Pxx      | <class 'list'> | 512  | 2048 |
    # | Pxx[0]   | float64        | -Inf | Inf  |
    # | Pxx[123] | float64        | -Inf | Inf  |
    # | Pxx[456] | float64        | -Inf | Inf  |
    # | Pxx[511] | float64        | -Inf | Inf  |

    # Power measurements are given in an array of frequency bins. The bins
    # are ordered Flo -> Fhi. The centre frequency of each bin is in f.
  