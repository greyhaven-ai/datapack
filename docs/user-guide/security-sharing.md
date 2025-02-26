# Security & Sharing

This guide covers how to secure your documents and share them safely with others using Datapack's built-in security features and sharing capabilities.

## Document Security

### Protecting Documents

Datapack provides several ways to protect your documents:

```python
from datapack import Document, SecurityOptions

# Create a document with security options
doc = Document(
    content="# Confidential Document\n\nThis document contains sensitive information.",
    metadata={
        "title": "Confidential Document",
        "author": "Security Team",
        "classification": "confidential"
    },
    security=SecurityOptions(
        encryption_enabled=True,
        password_protected=True,
        password="your-secure-password"  # Use a secure password in production
    )
)

# Save the protected document
doc.save("confidential_document.mdp")
```

### Access Control

You can implement access control for your documents:

```python
from datapack import Document, AccessControl, Permission, Role

# Define roles
viewer_role = Role("viewer", permissions=[Permission.READ])
editor_role = Role("editor", permissions=[Permission.READ, Permission.WRITE])
admin_role = Role("admin", permissions=[Permission.READ, Permission.WRITE, Permission.ADMIN])

# Create access control
access_control = AccessControl()
access_control.add_user("user1@example.com", viewer_role)
access_control.add_user("user2@example.com", editor_role)
access_control.add_user("admin@example.com", admin_role)

# Create a document with access control
doc = Document(
    content="# Protected Document\n\nThis document has access control.",
    metadata={
        "title": "Protected Document",
        "author": "Security Team"
    },
    access_control=access_control
)

# Save the document
doc.save("protected_document.mdp")
```

### Audit Logging

Track access and changes to your documents:

```python
from datapack import Document, AuditLogger
from datetime import datetime

# Create an audit logger
logger = AuditLogger(log_file="audit.log")

# Load a document
doc = Document.from_file("confidential_document.mdp", 
                        password="your-secure-password")

# Log access
logger.log_access(
    document_id=doc.id,
    user="user@example.com",
    action="view",
    timestamp=datetime.now(),
    ip_address="192.168.1.1"
)

# Make changes and log them
doc.content += "\n\n## New Section\n\nAdditional confidential information."
doc.save("confidential_document.mdp")

logger.log_change(
    document_id=doc.id,
    user="user@example.com",
    action="edit",
    timestamp=datetime.now(),
    ip_address="192.168.1.1",
    details="Added new section with confidential information"
)
```

## Document Sharing

### Sharing with Specific Users

Share documents with specific users or teams:

```python
from datapack import Document, SharingOptions

# Load a document
doc = Document.from_file("document.mdp")

# Configure sharing options
sharing = SharingOptions(
    recipients=["user1@example.com", "user2@example.com"],
    expiration_date="2023-12-31",
    allow_forwarding=False,
    access_level="view"  # Options: view, comment, edit
)

# Share the document
shared_url = doc.share(options=sharing)
print(f"Document shared with URL: {shared_url}")
```

### Creating Shared Document Collections

Create collections of related documents for sharing:

```python
from datapack import DocumentCollection, Document, SharingOptions

# Create a collection
collection = DocumentCollection("Project Documentation")

# Add documents to the collection
doc1 = Document.from_file("requirements.mdp")
doc2 = Document.from_file("design.mdp")
doc3 = Document.from_file("implementation.mdp")

collection.add(doc1)
collection.add(doc2)
collection.add(doc3)

# Configure sharing options for the collection
sharing = SharingOptions(
    recipients=["team@example.com"],
    expiration_date="2023-12-31",
    access_level="edit",
    require_authentication=True
)

# Share the collection
shared_collection_url = collection.share(options=sharing)
print(f"Collection shared with URL: {shared_collection_url}")
```

## Integration with Identity Management

Integrate with existing identity providers:

```python
from datapack import IdentityProvider, SecurityManager

# Configure identity provider
identity_provider = IdentityProvider(
    provider_type="oauth2",
    client_id="your-client-id",
    client_secret="your-client-secret",
    authorize_url="https://identity.example.com/oauth/authorize",
    token_url="https://identity.example.com/oauth/token",
    user_info_url="https://identity.example.com/oauth/userinfo"
)

# Create a security manager
security_manager = SecurityManager(identity_provider=identity_provider)

# Use the security manager for authentication and authorization
token = security_manager.authenticate(
    username="user@example.com",
    password="user-password"
)

# Check if user has access to a document
has_access = security_manager.check_access(
    document_id="doc-123",
    user_token=token,
    permission=Permission.READ
)

if has_access:
    doc = Document.from_file("protected_document.mdp", token=token)
    print(f"Access granted to: {doc.metadata.title}")
else:
    print("Access denied")
```

## Secure Document Transfer

Transfer documents securely between systems:

```python
from datapack import Document, SecureTransfer

# Load a document
doc = Document.from_file("confidential_document.mdp", 
                         password="your-secure-password")

# Create a secure transfer
transfer = SecureTransfer(
    encryption_key="your-encryption-key",
    destination="https://secure-api.example.com/documents"
)

# Transfer the document
transfer_result = transfer.send(doc)
print(f"Transfer status: {transfer_result.status}")
print(f"Transfer ID: {transfer_result.transfer_id}")
```

## Collaboration Features

### Real-time Collaboration

Enable real-time collaboration on documents:

```python
from datapack import Document, CollaborationSession

# Load a document
doc = Document.from_file("shared_document.mdp")

# Create a collaboration session
session = CollaborationSession(
    document=doc,
    session_id="session-123",
    owner="owner@example.com"
)

# Add collaborators
session.add_collaborator("user1@example.com", role="editor")
session.add_collaborator("user2@example.com", role="viewer")

# Start the session
session_url = session.start()
print(f"Collaboration session started: {session_url}")

# Monitor session activity
activity = session.get_activity()
print(f"Active users: {len(activity.active_users)}")
print(f"Changes made: {activity.change_count}")
```

### Review and Approval Workflows

Implement review and approval workflows:

```python
from datapack import Document, Workflow

# Load a document
doc = Document.from_file("document_for_review.mdp")

# Create a review workflow
workflow = Workflow(
    type="review_approval",
    document=doc,
    initiator="author@example.com"
)

# Add reviewers
workflow.add_step(
    name="Technical Review",
    assignees=["tech_reviewer@example.com"],
    deadline="2023-07-15"
)

workflow.add_step(
    name="Editorial Review",
    assignees=["editor@example.com"],
    deadline="2023-07-20"
)

workflow.add_step(
    name="Final Approval",
    assignees=["manager@example.com"],
    deadline="2023-07-25"
)

# Start the workflow
workflow_id = workflow.start()
print(f"Workflow started: {workflow_id}")

# Check workflow status
status = workflow.get_status()
print(f"Current step: {status.current_step}")
print(f"Completed steps: {status.completed_steps}")
print(f"Pending steps: {status.pending_steps}")
```

## Best Practices for Secure Document Handling

1. **Always Use Encryption** for sensitive documents
2. **Implement Proper Access Controls** based on the principle of least privilege
3. **Enable Audit Logging** to track document access and changes
4. **Set Expiration Dates** for shared documents
5. **Use Strong Authentication** including multi-factor when possible
6. **Regularly Review Access Permissions** to ensure they remain appropriate
7. **Train Users** on secure document handling practices
8. **Implement Data Loss Prevention** policies
9. **Backup Documents Securely** and test restoration procedures
10. **Comply with Relevant Regulations** such as GDPR, HIPAA, or CCPA

## Next Steps

Now that you understand Datapack's security and sharing features, you might want to explore:

- [Advanced Features](advanced-features.md) for more complex document operations
- [Integration](../integration/index.md) with other systems and services
- [API Reference](../api/core.md) for detailed API documentation 