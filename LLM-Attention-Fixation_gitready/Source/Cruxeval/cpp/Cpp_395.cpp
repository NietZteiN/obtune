#include<assert.h>
#include<bits/stdc++.h>
long f(std::string s) {
    for (int i = 0; i < s.size(); i++) {
        if (std::isdigit(s[i])) {
            return i + (s[i] == '0');
        } else if (s[i] == '0') {
            return -1;
        }
    }
    return -1;
}
int main() {
    auto candidate = f;
    assert(candidate(("11")) == (0));
}
