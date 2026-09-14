#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    if (std::all_of(s.begin(), s.end(), isalnum)) {
        return "True";
    }
    return "False";
}
int main() {
    auto candidate = f;
    assert(candidate(("777")) == ("True"));
}
