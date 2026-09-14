#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::transform(text.begin(), text.end(), text.begin(), ::tolower);
    return text.substr(0, 3);
}
int main() {
    auto candidate = f;
    assert(candidate(("mTYWLMwbLRVOqNEf.oLsYkZORKE[Ko[{n")) == ("mty"));
}
