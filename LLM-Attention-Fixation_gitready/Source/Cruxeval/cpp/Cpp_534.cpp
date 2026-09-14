#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string sequence, std::string value) {
    int i = std::max((int)(sequence.find(value) - sequence.size() / 3), 0);
    std::string result = "";
    for (int j = i; j < sequence.size(); ++j) {
        if (sequence[j] == '+') {
            result += value;
        } else {
            result += sequence[j];
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("hosu"), ("o")) == ("hosu"));
}
