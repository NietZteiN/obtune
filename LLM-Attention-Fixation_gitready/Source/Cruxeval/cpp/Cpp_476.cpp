#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string a, std::string split_on) {
    std::vector<char> t;
    for (char c : a) {
        t.push_back(c);
    }
    std::vector<char> result;
    for (char c : t) {
        if (c != ' ') {
            result.push_back(c);
        }
    }
    if (std::find(result.begin(), result.end(), split_on[0]) != result.end()) {
        return true;
    } else {
        return false;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("booty boot-boot bootclass"), ("k")) == (false));
}
