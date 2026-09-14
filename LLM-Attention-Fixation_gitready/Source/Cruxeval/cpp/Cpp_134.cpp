#include<assert.h>
#include<bits/stdc++.h>
std::string f(long n) {
    int t = 0;
    std::string b = "";
    std::vector<int> digits;
    std::string n_str = std::to_string(n);
    for (char c : n_str) {
        digits.push_back(c - '0');
    }

    for (int d : digits) {
        if (d == 0) {
            t++;
        } else {
            break;
        }
    }

    for (int i = 0; i < t; i++) {
        b += "104";
    }

    b += std::to_string(n);
    return b;
}
int main() {
    auto candidate = f;
    assert(candidate((372359)) == ("372359"));
}
