## Examples

### Example 1: Clear Documentation Available

**User:** "What are Stratus minions?"

**Process:**
1. Search: `search(cloudId="...", query="Stratus minions")`
2. Find: Confluence page "Stratus Architecture" + 3 Jira tickets
3. Fetch: Get full Confluence page content
4. Synthesize: Combine architectural overview with implementation details from tickets
5. Cite: Provide links to all sources

**Answer:**
```
Stratus minions are background worker processes that handle asynchronous task
processing in the Stratus system.

**Key Characteristics:**
- Run independently from web servers
- Process jobs from a Redis queue
- Can be scaled horizontally for increased throughput
- Handle tasks like email sending, report generation, and data processing

**Architecture:**
According to the Stratus Architecture documentation, minions follow a
worker-queue pattern where:
1. Web application enqueues tasks
2. Minions poll the queue for work
3. Tasks are processed asynchronously
4. Results are stored in the database

**Implementation Notes:**
From Jira ticket PROJ-203, the current deployment runs 5 minion instances,
with plans to scale to 10 for handling increased load.

## Sources
- [Stratus Architecture Guide](../link)
- [PROJ-203](../link) - Minion scaling implementation
```

### Example 2: Conflicting Information

**User:** "How long is our session timeout?"

**Process:**
1. Search across Confluence and Jira
2. Find: Docs say 30 min, but ticket reports actual timeout is 15 min
3. Fetch both sources for complete context
4. Clearly note the discrepancy

**Answer:**
```
There is a discrepancy between documented and actual behavior:

**Official Documentation** (Security Guidelines):
Session timeout is configured for 30 minutes of inactivity.

**Actual Behavior** (PROJ-456, reported Oct 2023):
Users are being logged out after 15 minutes due to a load balancer configuration
that overrides the application setting.

**Current Status:**
The engineering team is aware of this issue. The load balancer timeout needs to
be adjusted to match the application setting. No fix timeline has been set.

**Recommendation:** Plan for 15-minute timeout until this is resolved.

## Sources
- [Security Guidelines](../link) - Official documentation
- [PROJ-456](../link) - Timeout discrepancy bug report
```

### Example 3: Partial Information

**User:** "Explain our deployment process"

**Process:**
1. Search finds some information but not complete
2. Synthesize what is available
3. Note gaps in documentation

**Answer:**
```
Based on available documentation, here's what I found about the deployment process:

**Build Phase** (from Confluence "CI/CD Guide"):
1. Code pushed to main branch triggers GitHub Actions
2. Automated tests run (unit, integration)
3. Docker image built and pushed to registry

**Deployment Phase** (from Jira PROJ-789):
4. Staging deployment happens automatically
5. Manual approval required for production
6. Blue-green deployment strategy used

**Gaps in Documentation:**
I couldn't find documented information about:
- Rollback procedures
- Database migration handling
- Post-deployment verification steps

These details may exist in tribal knowledge or need to be documented.

## Sources
- [CI/CD Guide](../link)
- [PROJ-789](../link) - Deployment pipeline implementation

Would you like me to search for more specific aspects of deployment?
```

---
