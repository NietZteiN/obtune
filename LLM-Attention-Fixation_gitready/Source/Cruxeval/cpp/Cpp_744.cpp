#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string new_ending) {
    std::vector<char> result(text.begin(), text.end());
    result.insert(result.end(), new_ending.begin(), new_ending.end());
    return std::string(result.begin(), result.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("jro"), ("wdlp")) == ("jrowdlp"));
}
