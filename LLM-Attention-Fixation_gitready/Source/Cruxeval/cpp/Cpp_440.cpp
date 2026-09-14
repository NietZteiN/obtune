#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    if(std::all_of(text.begin(), text.end(), ::isdigit)) {
        return "yes";
    } else {
        return "no";
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("abc")) == ("no"));
}
