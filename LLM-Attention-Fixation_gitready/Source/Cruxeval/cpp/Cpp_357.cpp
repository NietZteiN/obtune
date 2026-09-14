#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    std::string r;
    for(int i = s.size() - 1; i >= 0; i--) {
        r += s[i];
    }
    return r;
}
int main() {
    auto candidate = f;
    assert(candidate(("crew")) == ("werc"));
}
