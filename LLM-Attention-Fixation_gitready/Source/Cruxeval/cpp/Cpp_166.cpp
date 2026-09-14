#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::map<std::string,std::string>> f(std::map<std::string,std::map<std::string,std::string>> graph) {
    std::map<std::string,std::map<std::string,std::string>> new_graph;
    for (auto const& [key, value] : graph) {
        new_graph[key] = {};
        for (auto const& subkey : value) {
            new_graph[key][subkey.first] = "";
        }
    }
    return new_graph;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::map<std::string,std::string>>())) == (std::map<std::string,std::map<std::string,std::string>>()));
}
