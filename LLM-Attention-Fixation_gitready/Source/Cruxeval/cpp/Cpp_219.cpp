#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string s1, std::string s2) {
    std::string new_s1 = s1;
    for (int k = 0; k < s2.size() + s1.size(); k++) {
        new_s1 += s1[0];
        if (new_s1.find(s2) != std::string::npos) {
            return true;
        }
    }
    return false;
}
int main() {
    auto candidate = f;
    assert(candidate(("Hello"), (")")) == (false));
}
