from datetime import datetime


class VisitTracker:
    """
    Tracks user visits and determines if they've reached their limit
    """
    
    def __init__(self, request):
        self.request = request
        self.session = request.session
        # Initialize visits tracking in session if not present
        if 'visit_count' not in self.session:
            self.session['visit_count'] = 0
            self.session['first_visit'] = datetime.now().isoformat()
            
    def get_visit_count(self):
        """Get the number of premium content visits for the current session"""
        return self.session.get('visit_count', 0)
    
    def increment_visit(self):
        """Increment the visit count for premium content access"""
        if self.is_anonymous():
            self.session['visit_count'] = self.get_visit_count() + 1
            self.session.modified = True
            
    def reset_visits(self):
        """Reset the visit counter, used when a user becomes paid"""
        self.session['visit_count'] = 0
        self.session.modified = True
            
    def is_anonymous(self):
        """Check if the user is anonymous or not authenticated"""
        return not self.request.user.is_authenticated
    
    def can_access_premium(self):
        """Check if the user can access premium content"""
        # Authenticated users: enforce 3-visit limit for free users, unlimited for paid/admin
        if self.request.user.is_authenticated:
            user = self.request.user
            # Admin or paid users have unlimited premium access
            if getattr(user, 'user_type', 'free') in ('admin', 'paid'):
                return True
            # Free users: limit to 3 premium accesses
            return getattr(user, 'free_access_count', 0) < 3

        # Anonymous users are limited to 3 visits per session
        return self.get_visit_count() < 3
    
    def needs_payment_prompt(self):
        """Check if the user needs to be prompted for payment"""
        # Only show payment prompt to anonymous users who've used up their free visits
        # or authenticated free users who've used up their free visits
        if self.request.user.is_authenticated:
            return (self.request.user.user_type == 'free' and 
                    self.request.user.free_access_count >= 3)
        else:
            return self.get_visit_count() >= 3
