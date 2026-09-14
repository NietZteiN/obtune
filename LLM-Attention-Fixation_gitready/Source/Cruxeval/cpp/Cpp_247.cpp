#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    if(std::all_of(s.begin(), s.end(), ::isalpha)) {
        return "yes";
    }
    if(s.empty()) {
        return "str is empty";
    }
    return "no";
}
int main() {
    auto candidate = f;
    assert(candidate(("Boolean")) == ("yes"));
}
