#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::vector<std::string> tokens;
    std::istringstream iss(text);
    std::string token;

    while (std::getline(iss, token, ',')) {
        tokens.push_back(token);
    }

    tokens.erase(tokens.begin());
    auto it = std::find(tokens.begin(), tokens.end(), "T");
    std::iter_swap(tokens.begin(), it);

    std::string result = "T,";
    for (const std::string& t : tokens) {
        result += t + ",";
    }

    result.pop_back(); // Remove the extra comma
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("Dmreh,Sspp,T,G ,.tB,Vxk,Cct")) == ("T,T,Sspp,G ,.tB,Vxk,Cct"));
}
