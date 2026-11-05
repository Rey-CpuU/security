# Web3 & Smart Contract Security Playbook

This playbook defines standard operational procedures, attack classes, and audit workflows for the **Web3 & Blockchain Security Auditor** role.

---

## 1. Web3 Audit Methodology

The Web3 Auditor follows a 5-phase testing and auditing pipeline:

```
[1. Threat Modeling & Invariant Extraction (x-ray)]
                      |
[2. Source Review & Manual Logic Audit (solidity-auditor, contract-auditor)]
                      |
[3. Stateful Invariant Fuzzing (fizz, Echidna, Medusa)]
                      |
[4. Arithmetic & Precision Analysis (dimensional-analysis)]
                      |
[5. Reporting, Invariant Patches & Proofs]
```

---

## 2. Core Smart Contract Vulnerability Classes

### 1. Reentrancy
* **Types**: Classic single-function reentrancy, cross-function reentrancy, cross-contract reentrancy, read-only reentrancy.
* **Mechanism**: State updates occurring *after* external calls (`call{value: ...}`) allowing an attacker contract's fallback/receive function to recursively invoke protocol functions with stale state.
* **Checks**:
  * Ensure Checks-Effects-Interactions (CEI) pattern is rigorously followed.
  * Verify `nonReentrant` modifiers (OpenZeppelin ReentrancyGuard).
  * Check read-only reentrancy on price query functions (`getVirtualPrice()`, `balanceOf()`).

### 2. Access Control & Authorization
* **Issues**: Missing `onlyOwner`, `onlyRole`, or uninitialized proxy implementations.
* **Checks**:
  * Unprotected initialization functions (`initialize()`) in upgradeable contracts (UUPS, Transparent).
  * Arbitrary `delegatecall` injection allowing attacker to overwrite storage slot 0 or `selfdestruct`.
  * Tx.origin authentication instead of `msg.sender` (vulnerable to phishing).

### 3. Oracle Manipulation & Flash Loans
* **Issues**: Relying on spot AMM reserves (`balanceOf(tokenA) / balanceOf(tokenB)`) for pricing rather than Time-Weighted Average Prices (TWAP) or Chainlink decentralized oracles.
* **Attack**: Attacker takes a flash loan, skews the pool reserves in a single block, triggers collateral liquidation or minting at distorted prices, and repays the flash loan in the same transaction.
* **Checks**:
  * Validate Chainlink heartbeat, round completion, and freshness (`answeredInRound >= roundId`, `updatedAt != 0`).
  * Check min/max circuit breaker bounds.

### 4. Arithmetic Precision & Decimal Scaling (WAD/RAY)
* **Issues**: Mixing tokens with different decimal precisions (e.g., USDC 6 decimals with DAI 18 decimals) without normalization.
* **Checks**:
  * Multiplication before division to prevent precision loss.
  * Correct scaling constants (`1e18` vs `1e27`).
  * Rounding direction: ensure protocol rounds against the user and in favor of protocol solvency (e.g., round debt up, round assets down).

---

## 3. Stateful Invariant Fuzzing with Fizz

### Step 1: Harness Generation
Run `fizz` to inspect Foundry/Hardhat contracts and scaffold the fuzzing harness under `test/fizz/`.

### Step 2: Invariant Assertion Mapping
Translate high-level protocol rules into executable assertions via `fizz-convert`:
* **Solvency Invariant**: Total internal user balances must never exceed the contract's actual token balance (`sum(userBalances) <= token.balanceOf(address(this))`).
* **Conservation of Mass**: Assets deposited + yield generated = assets redeemable.
* **Admin Privilege Invariant**: Non-admin callers cannot alter fees or pause the protocol.

### Step 3: Fuzzer Execution
Run Echidna or Medusa for 100,000+ call sequences:
```bash
echidna test/fizz/FuzzHarness.sol --config echidna.yaml
medusa fuzz
```

---

## 4. On-Chain Incident Investigation

When triaging a live on-chain exploit using `exploit-investigator`:
1. **Transaction Decomposition**: Parse input data, logs, internal calls, and balance deltas with Phalcon / Tenderly / Etherscan trace.
2. **Attacker Profiling**: Identify initial funding source (Tornado Cash, cross-chain bridge, CEX withdrawal).
3. **Vulnerability Pinpointing**: Identify the exact opcode or call that allowed abnormal profit.
4. **Impact Assessment**: Total Value Locked (TVL) drained, affected liquidity pools, and remaining risk in active contracts.
