#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> lines) {
    for(int i = 0; i < lines.size(); i++) {
        lines[i] = lines[i].append((lines.back().size() - lines[i].size()) / 2, ' ').insert(0, (lines.back().size() - lines[i].size()) / 2, ' ');
    }
    return lines;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"dZwbSR", (std::string)"wijHeq", (std::string)"qluVok", (std::string)"dxjxbF"}))) == (std::vector<std::string>({(std::string)"dZwbSR", (std::string)"wijHeq", (std::string)"qluVok", (std::string)"dxjxbF"})));
}
