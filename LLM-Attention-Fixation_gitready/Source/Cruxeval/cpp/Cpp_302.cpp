#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string) {
    std::string result = string;
    std::string toReplace = "needles";
    std::string replacement = "haystacks";
    size_t pos = result.find(toReplace);
    while (pos != std::string::npos) {
        result.replace(pos, toReplace.length(), replacement);
        pos = result.find(toReplace, pos + replacement.length());
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("wdeejjjzsjsjjsxjjneddaddddddefsfd")) == ("wdeejjjzsjsjjsxjjneddaddddddefsfd"));
}
