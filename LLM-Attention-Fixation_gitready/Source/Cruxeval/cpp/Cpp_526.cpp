#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string label1, std::string character, std::string label2, long index) {
    long m = label1.rfind(character);
    if (m >= index) {
        return label2.substr(0, m - index + 1);
    }
    return label1 + label2.substr(index - m - 1);
}
int main() {
    auto candidate = f;
    assert(candidate(("ekwies"), ("s"), ("rpg"), (1)) == ("rpg"));
}
