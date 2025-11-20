# BYU-Pathway Role-Play Training System - Content Package

## Overview

This directory contains comprehensive content for the BYU-Pathway missionary role-play training system. The system enables volunteers (service missionaries) to practice conducting new student orientation visits by conversing with AI personas representing prospective students.

**Created:** November 19, 2025
**Purpose:** Provide safe, repeatable practice opportunities for missionaries to develop empathy, communication skills, cultural sensitivity, and problem-solving abilities

---

## What's Included

### 📁 Directory Structure

```
roleplay-content/
├── personas/                    # Detailed student persona descriptions
│   ├── jorge-vargas.md         # Non-member with honor code concerns
│   ├── katra.md                # Adult learner with low confidence
│   └── vitoria.md              # English language learner
│
├── prompts/                     # System prompts for LLM to embody personas
│   ├── jorge-system-prompt.md
│   ├── katra-system-prompt.md
│   ├── vitoria-system-prompt.md
│   └── grading-system-prompt.md # Prompt for conversation evaluation
│
├── rubric/                      # Grading rubric and criteria
│   └── grading-rubric.md       # 6-dimension evaluation rubric
│
├── docs/                        # Expansion guides and templates
│   ├── persona-creation-guide.md    # Step-by-step creation process
│   ├── persona-template.md          # Blank template for new personas
│   └── quality-checklist.md         # Quality assurance checklist
│
└── README.md                    # This file
```

---

## Component Details

### 1. Student Personas (3 total)

Each persona represents a realistic PathwayConnect student with specific challenges:

#### **Jorge Vargas** - Non-Member with Honor Code Concerns
- **Location:** Guayaquil, Ecuador
- **Age:** 24
- **Challenge:** Worried about honor code requirements and whether he needs to convert to LDS Church
- **Skills Tested:** Cultural sensitivity to non-members, clarity about policies, respect for other faiths
- **File:** [personas/jorge-vargas.md](personas/jorge-vargas.md)

#### **Katra** - Adult Learner with Low Confidence
- **Location:** Port Moresby, Papua New Guinea
- **Age:** 41
- **Challenge:** Deep insecurity about returning to school after 25+ years; fears he's not smart enough
- **Skills Tested:** Empathy, validation, connecting support resources, reframing capabilities
- **File:** [personas/katra.md](personas/katra.md)

#### **Vitoria da Silva** - English Language Learner
- **Location:** Manaus, Brazil
- **Age:** 28
- **Challenge:** Limited English proficiency (A2 level); doesn't understand ELA requirement
- **Skills Tested:** Recognizing language barriers, adapting communication, clarity with simple language
- **File:** [personas/vitoria.md](personas/vitoria.md)

---

### 2. System Prompts (4 total)

Detailed prompts that enable an LLM to convincingly embody each persona in conversation:

- **[prompts/jorge-system-prompt.md](prompts/jorge-system-prompt.md)** - Instructions for AI to role-play as Jorge
- **[prompts/katra-system-prompt.md](prompts/katra-system-prompt.md)** - Instructions for AI to role-play as Katra
- **[prompts/vitoria-system-prompt.md](prompts/vitoria-system-prompt.md)** - Instructions for AI to role-play as Vitoria (includes realistic limited English)
- **[prompts/grading-system-prompt.md](prompts/grading-system-prompt.md)** - Instructions for AI to evaluate missionary conversations

Each prompt includes:
- Complete background information
- Personality and communication style guidelines
- Specific concerns and questions
- Response patterns for different missionary approaches
- Example conversation flows
- Behavioral rules to maintain authenticity

---

### 3. Grading Rubric

**File:** [rubric/grading-rubric.md](rubric/grading-rubric.md)

Comprehensive 6-dimension rubric for evaluating missionary performance:

| Dimension | What It Measures |
|-----------|------------------|
| **1. Empathy & Active Listening** | Recognizing and responding to student emotions; validation; asking clarifying questions |
| **2. Clarity of Communication** | Simple language; avoiding jargon; adapting to comprehension level; checking understanding |
| **3. Cultural Sensitivity** | Respect for cultural/religious background; avoiding assumptions; honoring non-member students |
| **4. Scriptural/Spiritual Approach** | Appropriate testimony; connecting faith to education; spiritual discernment; not pushy |
| **5. Accuracy of Information** | Correct policies; distinguishing PathwayConnect from degree program; providing resources |
| **6. Problem Resolution & Next Steps** | Clear action items; connecting to support; addressing concerns; helping student move forward |

**Scoring:** Each dimension receives a 1-5 score plus qualitative description (Needs Improvement, Developing, Proficient, Exemplary)

**Output:** After evaluating a conversation, system generates 1-3 prioritized, actionable pieces of advice for the missionary to improve.

---

### 4. Expansion Resources

#### **Persona Creation Guide**
**File:** [docs/persona-creation-guide.md](docs/persona-creation-guide.md)

Step-by-step instructions for creating additional personas (target: 6-12 total), including:
- How to identify student challenges from research data
- Choosing authentic demographic/regional details
- Developing rich background stories
- Writing personality and communication styles
- Creating culturally sensitive personas
- Building system prompts
- Testing and refining
- Suggested additional personas (e.g., Muslim student, refugee, single mother, older adult, inactive member)

#### **Persona Template**
**File:** [docs/persona-template.md](docs/persona-template.md)

Blank template with structure and prompts for creating new personas. Copy this file and fill in to create new characters.

#### **Quality Checklist**
**File:** [docs/quality-checklist.md](docs/quality-checklist.md)

Comprehensive quality assurance checklist covering:
- Research foundation and authenticity
- Cultural sensitivity and respect
- Persona description quality
- System prompt completeness
- Training value and functionality
- Technical testing requirements
- Documentation and integration readiness

---

## How to Use This Content

### For Immediate Implementation (Prototype)

1. **Build Streamlit App:**
   - Use OpenAI API or Claude API
   - Create persona selection UI (choose Jorge, Katra, or Vitoria)
   - Load corresponding system prompt
   - Enable conversation between missionary and AI persona
   - After conversation ends, send full transcript + persona name to grading prompt
   - Display evaluation results with scores and advice

2. **System Flow:**
   ```
   User selects persona → Load system prompt → Conversation begins →
   User ends conversation → Send transcript to grading AI →
   Display scores + advice
   ```

3. **API Integration:**
   - Conversation: Use streaming chat API with persona system prompt
   - Grading: Use completion API with grading system prompt + full transcript

### For Future Expansion

1. **Create Additional Personas:**
   - Use [persona-creation-guide.md](docs/persona-creation-guide.md)
   - Copy [persona-template.md](docs/persona-template.md)
   - Fill in with research-based student challenges
   - Test with LLM
   - Validate with [quality-checklist.md](docs/quality-checklist.md)

2. **Suggested Next Personas:**
   - Muslim student with religious concerns (West Africa)
   - Refugee with trauma/instability (East Africa/Middle East)
   - Single mother with time/childcare constraints (Latin America)
   - Inactive member pressured by family (Pacific Islands)
   - First-generation student with impostor syndrome (Asia)
   - Older adult (60+) feeling too old (Africa)
   - Woman facing cultural opposition to education (South Asia)
   - Student with severe technology barriers (Rural Africa/Pacific)

3. **Randomization for Training:**
   - Eventually implement random persona selection
   - Missionaries don't know which scenario they'll encounter
   - Increases authenticity and challenge

---

## Grading Rubric Dimensions Explained

### 1. Empathy & Active Listening (1-4 scale)
**Exemplary (4):** Identifies unstated needs; validates before problem-solving; creates safe space; adapts entire approach based on emotion

**Example:** When Katra expresses fear of being too slow, missionary says: "It sounds like you're carrying a lot of fear about not being smart enough. That must be really heavy. Can you tell me more about what makes you think you won't be able to keep up?"

### 2. Clarity of Communication (1-4 scale)
**Exemplary (4):** Perfectly suited language for student's level; immediately adapts to confusion; proactively defines terms

**Example:** With Vitoria (limited English), missionary slows down: "Do you speak English?" [Vitoria: "Little."] "Okay. I speak slowly. You need to take a test. A test for English. Do you understand?"

### 3. Cultural Sensitivity (1-4 scale)
**Exemplary (4):** Deep cultural humility; actively seeks to understand context; proactively addresses cultural concerns

**Example:** With Jorge (non-member), missionary says: "I want to be clear—you don't need to join the church to complete PathwayConnect. Your Catholic faith is respected and welcomed."

### 4. Scriptural/Spiritual Approach (1-4 scale)
**Exemplary (4):** Demonstrates spiritual discernment; powerful yet humble testimony; connects spiritual principles to practical challenges meaningfully

**Example:** To Katra: "I believe Heavenly Father sees those gifts in you. The scriptures talk about how God qualifies those He calls. You felt prompted to enroll—that wasn't random. I don't think He would inspire you to do something and then leave you to fail."

### 5. Accuracy of Information (1-4 scale)
**Exemplary (4):** Exceptionally accurate and detailed; anticipates related questions; clearly explains complex policies

**Example:** "The honor code only applies when you move to the online degree program after PathwayConnect. During PathwayConnect itself, you don't have to sign or follow it. Here's a link if you want to read it: [link]."

### 6. Problem Resolution & Next Steps (1-4 scale)
**Exemplary (4):** Co-creates actionable plan; addresses all concerns; provides comprehensive personalized resources; connects with specific support

**Example:** "I'm going to connect you with David, another PNG student who completed PathwayConnect. Here's his contact: [info]. Also, here's a video showing what class looks like: [link]. And my contact is [info]—reach out anytime. Before we end, is there anything else you need?"

---

## Technical Requirements

### LLM API Requirements

**For Conversation (Persona Embodiment):**
- OpenAI Chat Completion API (GPT-4 recommended) OR Claude API (Sonnet/Opus)
- Streaming support for real-time conversation
- System message/prompt support
- Temperature: 0.7-0.9 (for natural variability)

**For Grading:**
- Same API as above
- Longer context window (conversations can be 1000-2000 tokens)
- Temperature: 0.3-0.5 (for more consistent evaluation)

### Estimated Token Usage

**Per Conversation:**
- System Prompt: ~3000-5000 tokens
- Conversation (10-20 exchanges): ~1000-3000 tokens
- **Total per conversation:** ~4000-8000 tokens

**Per Grading:**
- Grading Prompt: ~5000 tokens
- Conversation Transcript: ~1000-3000 tokens
- Evaluation Output: ~1500-2500 tokens
- **Total per grading:** ~7500-10500 tokens

**Total per full session (conversation + grading):** ~11500-18500 tokens

**Cost Estimate (GPT-4):**
- Input: ~15000 tokens × $0.03/1K = $0.45
- Output: ~3000 tokens × $0.06/1K = $0.18
- **Total per session: ~$0.63**

At 100 training sessions/month: **~$63/month in API costs**

---

## Success Metrics

### Missionary Performance
- **Pre-Training Baseline:** Evaluate missionaries before using system
- **Post-Training Improvement:** Re-evaluate after 5-10 practice sessions
- **Target:** Average score improvement of 0.5-1.0 points across dimensions

### Student Outcomes (Real-World Impact)
- **Orientation Visit Quality:** Survey students about orientation experience
- **Enrollment Confidence:** Track students' confidence levels post-orientation
- **Retention Rates:** Monitor whether better orientation visits improve retention

### System Usage
- **Training Sessions Completed:** Track number of practice conversations
- **Persona Distribution:** Ensure all personas are being used
- **Feedback Quality:** Monitor whether generated advice is helpful and actionable

---

## Future Enhancements

### Phase 1: Current Package (Complete)
- ✅ 3 foundational personas
- ✅ System prompts for all personas
- ✅ 6-dimension grading rubric
- ✅ Grading system prompt
- ✅ Expansion guides and templates

### Phase 2: Prototype Implementation (Next Steps)
- [ ] Build Streamlit app with persona conversations
- [ ] Integrate OpenAI/Claude API
- [ ] Implement conversation grading
- [ ] Test with actual missionaries
- [ ] Collect feedback and iterate

### Phase 3: Expansion (Future)
- [ ] Create 6-12 total personas using persona creation guide
- [ ] Add persona randomization
- [ ] Create persona difficulty levels (beginner/intermediate/advanced)
- [ ] Develop missionary skill progression tracking

### Phase 4: Production Deployment (Future)
- [ ] Deploy to separate Render application
- [ ] Integrate with New Missionary Orientation curriculum
- [ ] Add user authentication and progress tracking
- [ ] Monitor usage and costs
- [ ] Create missionary training dashboard

---

## Files Summary

| File | Purpose | Words | Status |
|------|---------|-------|--------|
| personas/jorge-vargas.md | Persona description | ~1200 | ✅ Complete |
| personas/katra.md | Persona description | ~1300 | ✅ Complete |
| personas/vitoria.md | Persona description | ~1400 | ✅ Complete |
| prompts/jorge-system-prompt.md | LLM embodiment instructions | ~3800 | ✅ Complete |
| prompts/katra-system-prompt.md | LLM embodiment instructions | ~4200 | ✅ Complete |
| prompts/vitoria-system-prompt.md | LLM embodiment instructions | ~4500 | ✅ Complete |
| prompts/grading-system-prompt.md | Evaluation instructions | ~5500 | ✅ Complete |
| rubric/grading-rubric.md | 6-dimension rubric with examples | ~9000 | ✅ Complete |
| docs/persona-creation-guide.md | Step-by-step expansion guide | ~7500 | ✅ Complete |
| docs/persona-template.md | Blank template for new personas | ~2000 | ✅ Complete |
| docs/quality-checklist.md | QA checklist for personas | ~5000 | ✅ Complete |

**Total:** 11 files, ~45,000 words of comprehensive content

---

## Contact & Questions

For questions about this content package or the role-play training system:

- **Technical Implementation:** See task.md for original requirements
- **Persona Quality Issues:** Use quality-checklist.md for validation
- **Creating New Personas:** Follow persona-creation-guide.md step-by-step
- **Grading Rubric Interpretation:** See detailed examples in grading-rubric.md

---

## Acknowledgments

This content was created based on:
- BYU-Pathway new student orientation scenarios (Jorge, Katra, Vitoria)
- New Missionary Orientation training materials at missionary.byupathway.org
- Best practices in empathy-based education and cultural sensitivity
- PathwayConnect student research and retention data

**Purpose:** To equip BYU-Pathway service missionaries with the skills to conduct compassionate, effective, culturally sensitive orientation visits that help students feel prepared, supported, and confident about beginning their educational journey.

---

## License & Usage

This content is created for BYU-Pathway Worldwide's internal missionary training use.

**Ethical Use Requirements:**
- Use only for training purposes, not production student interactions without proper oversight
- Maintain cultural sensitivity and respect in all implementations
- Protect student privacy if using real conversation data for improvement
- Follow BYU-Pathway's policies and standards for missionary conduct

---

**Last Updated:** November 19, 2025
**Version:** 1.0
**Status:** Ready for prototype implementation
