#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string changes) {
    std::string result = "";
    int count = 0;
    std::vector<char> changesVec(changes.begin(), changes.end());
    for (char& c : text) {
        result += (c == 'e' ? c : changesVec[count % changesVec.size()]);
        count += (c != 'e' ? 1 : 0);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("fssnvd"), ("yes")) == ("yesyes"));
}
