#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::replace(text.begin(), text.end(), '#', '1');
    std::replace(text.begin(), text.end(), '$', '5');
    return std::all_of(text.begin(), text.end(), ::isdigit) ? "yes" : "no";
}
int main() {
    auto candidate = f;
    assert(candidate(("A")) == ("no"));
}
