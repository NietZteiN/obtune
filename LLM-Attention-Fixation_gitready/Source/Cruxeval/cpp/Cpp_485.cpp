#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string tokens) {
    std::vector<std::string> tokens_split;
    std::istringstream iss(tokens);
    for(std::string tokens; iss >> tokens; )
        tokens_split.push_back(tokens);

    if(tokens_split.size() == 2)
        std::reverse(tokens_split.begin(), tokens_split.end());

    std::stringstream ss;
    ss << std::left << std::setw(5) << tokens_split[0] << " ";
    ss << std::left << std::setw(5) << tokens_split[1];

    return ss.str();
}
int main() {
    auto candidate = f;
    assert(candidate(("gsd avdropj")) == ("avdropj gsd  "));
}
