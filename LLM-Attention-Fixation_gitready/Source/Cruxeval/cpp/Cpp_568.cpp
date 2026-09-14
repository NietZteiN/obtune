#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string num) {
    int letter = 1;
    for (char i : "1234567890") {
        size_t pos = num.find(i);
        if (pos != std::string::npos) {
            num.erase(pos, 1);
        }
        if (num.empty()) {
            break;
        }
        if (letter >= num.size()) {
            letter = 0;
        }
        num = num.substr(letter) + num.substr(0, letter);
        letter += 1;
    }
    return num;
}
int main() {
    auto candidate = f;
    assert(candidate(("bwmm7h")) == ("mhbwm"));
}
