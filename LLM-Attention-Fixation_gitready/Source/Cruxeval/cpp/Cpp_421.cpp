#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, long n) {
    if (s.length() < n) {
        return s;
    } else {
        return s.substr(n);
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("try."), (5)) == ("try."));
}
