#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    try {
        while (text.find("nnet lloP") != std::string::npos) {
            text = text.replace(text.find("nnet lloP"), 10, "nnet loLp");
        }
    } catch (...) {
        // handle exceptions if needed
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("a_A_b_B3 ")) == ("a_A_b_B3 "));
}
