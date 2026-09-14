#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::istringstream iss(text);
    std::string word;
    while (iss >> word) {
        if (!std::all_of(word.begin(), word.end(), ::isdigit)) {
            return "no";
        }
    }
    return "yes";
}
int main() {
    auto candidate = f;
    assert(candidate(("03625163633 d")) == ("no"));
}
