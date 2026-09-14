#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string sentences) {
    std::stringstream ss(sentences);
    std::string sentence;
    while (std::getline(ss, sentence, '.')) {
        if (std::all_of(sentence.begin(), sentence.end(), ::isdigit)) {
            return "oscillating";
        }
    }
    return "not oscillating";
}
int main() {
    auto candidate = f;
    assert(candidate(("not numbers")) == ("not oscillating"));
}
