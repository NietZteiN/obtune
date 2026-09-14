#include<assert.h>
#include<bits/stdc++.h>
long f(std::string s) {
    std::string b = "";
    std::string c = "";
    for (char i : s) {
        c = c + i;
        if (s.rfind(c) != std::string::npos) {
            return s.rfind(c);
        }
    }
    return 0;
}
int main() {
    auto candidate = f;
    assert(candidate(("papeluchis")) == (2));
}
