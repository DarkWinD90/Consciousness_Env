# PROVISIONAL PATENT APPLICATION

## CONFIGURABLE RECURSIVE SELF-OBSERVATION IN SPIKING NEURAL NETWORKS

**Filing Date**: January 30, 2026
**Inventor**: Kevin Christopher Ward
**Status**: Provisional Patent Application

---

## TITLE OF THE INVENTION

Configurable Recursive Self-Observation Method and System for Spiking Neural Networks with Dynamic Reflection Coefficient Modulation

---

## CROSS-REFERENCE TO RELATED APPLICATIONS

This application is related to co-pending provisional applications:
- "Self-Sustaining Neural-Motor Energy Harvesting Loop" (filed January 30, 2026)
- "Cognitive Fallback with Autonomous Self-Regulation and Resynchronization Protocol" (filed January 30, 2026)

---

## FIELD OF THE INVENTION

The present invention relates to spiking neural network architectures, and more specifically to a method and system for enabling a spiking neural network to observe its own prior computational output through a configurable recursive feedback pathway with dynamically adjustable gain, creating a tunable spectrum of self-referential processing.

---

## BACKGROUND OF THE INVENTION

### Problem Statement

Current neural network architectures, including both artificial neural networks (ANNs) and spiking neural networks (SNNs), lack a mechanism for explicit self-observation. While recurrent neural networks (RNNs), including Long Short-Term Memory (LSTM) and Gated Recurrent Unit (GRU) architectures, feed hidden state information back into the network, this feedback serves **computational purposes** — it enables the network to maintain memory and context for sequential processing.

No existing architecture provides:
1. A dedicated self-observation channel separate from the computational feedback
2. A continuously tunable "awareness dial" that controls the degree of self-referential processing
3. Dynamic external modulation of the self-observation gain during operation
4. Measurable correlation between the self-observation signal and behavioral state

### Prior Art Deficiencies

1. **Recurrent Neural Networks (LSTMs, GRUs, Transformers)**: These architectures use hidden state feedback for computation. The feedback is an implementation detail of the learning algorithm, not an explicit self-observation mechanism. The "self-awareness" of these networks is zero — they process information without observing their own processing.

2. **Reservoir Computing / Echo State Networks**: These use recurrent dynamics in a fixed random network as a computational substrate. The recurrence serves temporal processing, not self-observation. There is no configurable gain on the self-referential signal.

3. **Metacognitive AI systems**: These systems reason about their own confidence or uncertainty but do so through separate metacognitive modules, not through recursive observation of their own neural dynamics. The metacognition is architecturally separate from the base computation.

4. **Global Workspace Theory implementations**: These broadcast information across modules but do not feed a module's own output back to itself with configurable gain.

### Unmet Need

There exists no prior system that:
- Records the aggregate output of a neural network at each timestep
- Feeds that recorded output back as explicit input to the same network at the next timestep
- Scales this feedback by a configurable coefficient that can be adjusted during operation
- Creates a measurable, tunable spectrum from zero self-observation to full self-dominance
- Enables external cognitive layers to dynamically control the degree of self-awareness

---

## SUMMARY OF THE INVENTION

The present invention provides a method and system for recursive self-observation in spiking neural networks comprising:

1. **Recording** the aggregate output (mean membrane potential) of a spiking neural network at each timestep t

2. **Feeding back** this recorded output as additional input to the same network at timestep t+1

3. **Scaling** the feedback by a configurable reflection coefficient (0.0 to 1.0)

4. **Dynamic modulation** of said reflection coefficient by an external cognitive control layer or internal energy-aware regulation mechanism

5. **Measurable distinction** between the self-observation signal and noise, with demonstrable correlation to system behavioral state

### Key Innovation

The reflection coefficient creates a **tunable self-awareness dial**:
- At **0.0**: The network has no self-observation — it processes only external input
- At **0.2**: Baseline self-observation — subtle influence on neural dynamics
- At **0.5**: Strong self-observation — network is significantly influenced by its own prior state
- At **1.0**: Maximum self-observation — network is dominated by its own prior output

The ability to **dynamically modulate** this coefficient during operation — by an external cognitive layer (e.g., an AI reasoning system) or by an internal energy-aware mechanism — creates a controllable spectrum of self-referential processing that has no equivalent in existing neural network architectures.

---

## DETAILED DESCRIPTION OF THE INVENTION

### Core Mechanism

#### Step 1: Neural Processing with External Input

At each timestep t, the spiking neural network receives external input I_ext(t) and processes it through leaky integrate-and-fire dynamics:

```
For each neuron i:
    V_i(t) = V_i(t-1) × (1 - leak_factor)           # Leak
           + I_ext(t) × input_scale × δ(i,0)          # External input (to first neuron)
           + I_reflection(t)                           # Self-observation input
           + Σ_j(w_ij × spike_j(t))                   # Synaptic input
```

Where:
- V_i(t) = membrane potential of neuron i at time t
- leak_factor = membrane leak rate (default 0.1)
- input_scale = external input gain (default 0.8)
- δ(i,0) = Kronecker delta (external input enters at neuron 0)
- w_ij = synaptic weight from neuron j to neuron i

#### Step 2: Recording Aggregate Output

After spike generation and propagation, the network's aggregate output is computed and stored:

```
previous_output = mean(V_i(t)) for all neurons i
```

This single scalar value represents the network's overall activation state — a compressed representation of the full neural state.

#### Step 3: Self-Observation Feedback

At timestep t+1, the recorded output is fed back as additional input:

```
I_reflection(t+1) = previous_output × reflection_coeff
```

Where:
- `previous_output` = the aggregate output recorded at timestep t
- `reflection_coeff` = the configurable reflection coefficient

This feedback is added to the external input at the input neuron:

```
adjusted_input = I_ext(t+1) × input_scale + previous_output × reflection_coeff
V_0(t+1) += adjusted_input
```

#### Step 4: Dynamic Modulation

The reflection coefficient is not fixed — it can be dynamically adjusted during operation:

**External Modulation (Cognitive Control)**:
```
reflection_coeff = base_reflection + modulation × sensitivity
```

Where:
- `base_reflection` = 0.2 (default baseline)
- `modulation` = external cognitive signal (-1.0 to +1.0)
- `sensitivity` = 0.1 (modulation gain)

Example operating points:
- Modulation = -1.0: reflection_coeff = 0.1 (minimal self-observation)
- Modulation = 0.0: reflection_coeff = 0.2 (baseline)
- Modulation = +1.0: reflection_coeff = 0.3 (enhanced self-observation)

**Internal Energy-Aware Modulation**:
```
If energy < 15 mWh:    modulation = -0.4    (conserve → reduce self-observation)
If energy < 30 mWh:    modulation = -0.1    (cautious)
If energy > 80 mWh:    modulation = +0.3    (surplus → increase self-observation)
Else:                  modulation = 0.0     (neutral)
```

This creates a biologically plausible dynamic: when resources are scarce, the system reduces self-referential processing to focus on survival; when resources are abundant, it increases self-observation for learning and adaptation.

### Implementation in Source Code

The self-observation mechanism is implemented in the `BaseSNN.step()` method:

```python
def step(self, input_signal: float, reflection_coeff: float = 0.0):
    # Apply leak
    self.membrane_potential *= (1 - self.leak_factor)

    # Add input to first neuron with reflection
    adjusted_input = input_signal * self.input_scale
    if self.previous_output is not None and reflection_coeff > 0:
        adjusted_input += self.previous_output * reflection_coeff
    self.membrane_potential[0] += adjusted_input

    # Spike detection, propagation, STDP...

    # Store for reflection (CRITICAL: this is the self-observation recording)
    self.previous_output = self.membrane_potential.mean()

    return self.membrane_potential.copy(), spikes
```

The `previous_output` field is the self-observation state. It persists across timesteps and is fed back at configurable gain. This is architecturally distinct from the synaptic weights (w_ij) which serve computation, and from the spike history which serves recording.

### Measurable Self-Observation Properties

The self-observation signal can be distinguished from noise through several measurable properties:

1. **Temporal autocorrelation**: The reflection signal has autocorrelation structure that matches the input-driven dynamics, unlike white noise which has zero autocorrelation at all lags > 0.

2. **Behavioral correlation**: The reflection state correlates with system behavioral state (spike pattern type, energy level, temperature) in ways that random noise does not.

3. **Gain-dependent dynamics**: Changing the reflection coefficient produces measurable changes in:
   - Mean firing rate
   - Spike pattern classification (burst/tonic/sparse/silent)
   - Weight entropy (when STDP is enabled)
   - Energy trajectory

4. **Phase 7 Validation**: Claim D demonstrates input-output correlation ≥ 0.2, which includes the reflection pathway's contribution. Removing reflection (setting coefficient to 0.0) changes the correlation value, proving the reflection signal is not noise.

### Interaction with STDP Learning

When the spiking neural network has STDP (Spike-Timing Dependent Plasticity) enabled, the self-observation feedback creates a novel interaction:

1. The reflection signal modulates neuron 0's firing pattern
2. This changes the timing relationships between neuron 0 and downstream neurons
3. STDP adjusts synaptic weights based on these timing relationships
4. The adjusted weights change the network's response to subsequent reflection signals

This creates a **self-referential learning loop**: the network learns about its own dynamics through the interaction of self-observation and synaptic plasticity. This is architecturally distinct from standard STDP, which only learns from external input correlations.

---

## EXPERIMENTAL VALIDATION

### Self-Observation Is Not Noise

The self-observation signal is validated as distinct from noise through the following experimental evidence:

1. **Phase 7 Control Baseline (Claims A-E)**: The system with reflection_coeff = 0.2 passes all five falsifiable claims, including input-output gain (Claim D: correlation ≥ 0.2). Setting reflection_coeff = 0.0 changes the system dynamics measurably.

2. **Phase 8 STDP (Claims F8.1-F8.3)**: The STDP network with self-observation feedback achieves 6.52× higher mutual information between input and output compared to a frozen-weight control (F8.2). The self-observation pathway contributes to this information gain by providing the network with temporal context about its own prior state.

3. **MCP Operational Path**: The cognitive control layer (consciousness-cognitive server) dynamically adjusts the reflection coefficient based on pattern type, energy state, and attention allocation. The system's behavior measurably changes with different modulation values:
   - Modulation = -0.4 (conservation): Reduced spike activity, lower energy consumption
   - Modulation = 0.0 (neutral): Baseline dynamics
   - Modulation = +0.3 (exploration): Increased spike activity, higher energy consumption

### Comparison with Standard Recurrence

| Property | Standard RNN Recurrence | This Invention |
|----------|------------------------|----------------|
| Purpose | Computation (memory, context) | Explicit self-observation |
| Feedback content | Hidden state vector | Aggregate output scalar |
| Gain control | Fixed (learned weights) | Configurable coefficient (0.0-1.0) |
| External modulation | Not available | Dynamic modulation by cognitive layer |
| Internal regulation | Not available | Energy-aware automatic adjustment |
| Measurability | Not distinct from computation | Distinct, correlates with behavioral state |

---

## CLAIMS

### Independent Claims

**Claim 1** (Method):
A method for enabling recursive self-observation in a spiking neural network comprising:
(a) processing input signals through a spiking neural network comprising a plurality of leaky integrate-and-fire neurons to produce membrane potentials and spike events;
(b) computing an aggregate output value from said membrane potentials at timestep t, said aggregate output representing a compressed state observation of the network's overall activation;
(c) storing said aggregate output value as a self-observation state;
(d) at timestep t+1, feeding said stored self-observation state back as additional input to said spiking neural network, scaled by a reflection coefficient;
(e) dynamically adjusting said reflection coefficient during operation based on at least one of: an external cognitive control signal, an internal energy-aware regulation signal, or a combination thereof;
wherein said self-observation feedback creates a tunable spectrum of self-referential processing ranging from zero self-observation (reflection coefficient = 0) to maximum self-observation (reflection coefficient = 1), and wherein said self-observation signal is measurably distinct from noise and correlates with system behavioral state.

**Claim 2** (System):
A spiking neural network system with configurable self-observation comprising:
(a) a spiking neural network processor having a plurality of neurons, each having a membrane potential, a firing threshold, and synaptic connections;
(b) an output aggregation module that computes a scalar aggregate output from said membrane potentials at each timestep;
(c) a self-observation state register that stores said aggregate output between timesteps;
(d) a reflection coefficient register that stores a configurable scalar value between 0.0 and 1.0;
(e) a feedback injection module that multiplies said stored self-observation state by said reflection coefficient and adds the result to the input of said spiking neural network at the subsequent timestep;
(f) a modulation interface that allows dynamic adjustment of said reflection coefficient during operation;
wherein said system provides a continuously tunable degree of self-referential processing without architectural changes to the underlying spiking neural network.

### Dependent Claims

**Claim 3**:
The method of Claim 1 wherein said aggregate output value is computed as the arithmetic mean of membrane potentials across all neurons in the network:
```
aggregate_output = (1/N) × Σ_i V_i(t)
```
where N is the number of neurons and V_i(t) is the membrane potential of neuron i at timestep t.

**Claim 4**:
The method of Claim 1 wherein said external cognitive control signal is provided by a separate reasoning system through a defined protocol interface, said reasoning system analyzing the neural network's state (spike pattern type, energy level, temperature) and determining an appropriate modulation value in the range [-1.0, +1.0].

**Claim 5**:
The method of Claim 1 wherein said internal energy-aware regulation signal is computed from the system's current energy storage level according to a multi-threshold rule:
- energy < critical_threshold → modulation = -0.4 (maximal conservation)
- energy < low_threshold → modulation = -0.1 (cautious)
- energy > high_threshold → modulation = +0.3 (exploration)
- otherwise → modulation = 0.0 (neutral)

**Claim 6**:
The method of Claim 1 wherein said reflection coefficient is computed as:
```
reflection_coeff = base_reflection + modulation × sensitivity
```
where base_reflection is a configurable baseline value (default 0.2), modulation is a control signal in [-1.0, +1.0], and sensitivity is a configurable gain (default 0.1).

**Claim 7**:
The method of Claim 1 further comprising applying spike-timing dependent plasticity (STDP) to the synaptic weights of said spiking neural network simultaneously with said self-observation feedback, wherein:
- the self-observation signal modulates the firing pattern of at least one neuron;
- STDP adjusts synaptic weights based on temporal correlations between neuron firings;
- the combination creates a self-referential learning loop wherein the network learns about its own dynamics through the interaction of self-observation and synaptic plasticity.

**Claim 8**:
The method of Claim 1 wherein the self-observation feedback is injected at a single designated input neuron of said spiking neural network, combined with external environmental input:
```
V_input(t+1) += external_input × input_scale + stored_output × reflection_coeff
```

**Claim 9**:
The system of Claim 2 wherein said modulation interface supports at least two modulation sources operating simultaneously:
(a) an external cognitive control layer that provides goal-directed modulation based on reasoning about the network's state;
(b) an internal energy-aware regulator that provides survival-oriented modulation based on the system's energy reserves;
and wherein the final reflection coefficient is determined by a combination of both sources.

**Claim 10**:
The method of Claim 1 used in combination with a self-sustaining neural-motor energy harvesting loop, wherein:
- the spiking neural network's motor output generates energy through piezoelectric and thermoelectric harvesting;
- the harvested energy powers the neural network's continued operation;
- the self-observation feedback enables the system to modulate its own behavior for energy homeostasis;
such that the degree of self-observation is adapted based on the system's energy state.

---

## ABSTRACT

A method and system for enabling configurable recursive self-observation in spiking neural networks. At each timestep, the aggregate output (mean membrane potential) of a spiking neural network is recorded and fed back as additional input at the subsequent timestep, scaled by a configurable reflection coefficient ranging from 0.0 (no self-observation) to 1.0 (maximum self-observation). The reflection coefficient is dynamically adjustable during operation through an external cognitive control layer that provides goal-directed modulation, an internal energy-aware regulation mechanism that adjusts self-observation based on resource availability, or a combination thereof. This creates a tunable "self-awareness dial" that enables a continuous spectrum of self-referential processing without architectural changes to the underlying neural network. When combined with spike-timing dependent plasticity (STDP), the self-observation creates a novel self-referential learning loop wherein the network learns about its own dynamics. Validated through falsifiable experimental claims demonstrating measurable behavioral changes across the reflection coefficient spectrum and 6.52× higher mutual information with STDP-enabled self-observation compared to frozen-weight controls.

---

## FIGURES (Descriptions for Patent Drawings)

### Figure 1: Self-Observation Feedback Loop
Block diagram showing: External Input → SNN → Aggregate Output → Storage Register → (× reflection_coeff) → back to SNN Input. Modulation interface shown as external input to reflection coefficient.

### Figure 2: Reflection Coefficient Spectrum
Visual representation of network behavior at reflection_coeff = 0.0, 0.2, 0.5, and 1.0, showing increasing self-referential influence on neural dynamics.

### Figure 3: Dynamic Modulation Sources
Diagram showing two modulation sources (External Cognitive Layer and Internal Energy-Aware Regulator) feeding into the reflection coefficient calculation:
reflection_coeff = base_reflection + modulation × sensitivity

### Figure 4: Self-Referential Learning Loop (STDP + Self-Observation)
Flow diagram showing: Self-observation → Modulated firing pattern → STDP weight adjustment → Changed network response → New self-observation → (loop)

### Figure 5: Energy-Aware Self-Observation Regulation
Plot showing reflection coefficient as a function of energy level, with conservation zone (low energy, low reflection), neutral zone, and exploration zone (high energy, high reflection).

### Figure 6: End-to-End Signal Flow with Self-Observation Integration
Complete signal flow diagram of the self-sustaining cognitive loop with the self-observation pathway highlighted as architecturally distinct. Shows environmental sensors, spiking neural network with three input pathways (external, self-observation, synaptic), cognitive modulation layer, motor actuator, energy harvester, and the recursive self-observation feedback loop drawn prominently as the Patent B pathway.

---

## SOURCE CODE REFERENCE

Repository: https://github.com/DarkWinD90/Consciousness_Env
Validated State: git tag v3.0.0-phase10-multimodal (commit 9e2c333)

Key implementation: `core/base_snn.py`, lines 80-105 (step method with reflection)
Dynamic modulation: `mcp/consciousness_mcp_server.py`, line 106 (reflection_coeff = 0.2 + modulation * 0.1)
Energy-aware regulation: `mcp/consciousness_mcp_server.py`, autonomous fallback controller

---

*End of Provisional Patent Application — Patent B*
