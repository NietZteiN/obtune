#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string s) {
    std::vector<char> l(s.begin(), s.end());
    for (int i = 0; i < l.size(); i++) {
        l[i] = tolower(l[i]);
        if (!isdigit(l[i])) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate(("")) == (true));
}
