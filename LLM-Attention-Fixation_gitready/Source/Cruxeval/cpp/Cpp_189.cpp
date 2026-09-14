#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string out, std::map<std::string,std::vector<std::string>> mapping) {
    for (auto& [key, value] : mapping) {
        for (auto& el : value) {
            std::string placeholder = "{" + key + "}";
            size_t pos = out.find(placeholder);
            if (pos != std::string::npos) {
                out.replace(pos, placeholder.length(), value[0]);
                std::reverse(value[0].begin(), value[0].end());
            }
        }
    }
    return out;
}
int main() {
    auto candidate = f;
    assert(candidate(("{{{{}}}}"), (std::map<std::string,std::vector<std::string>>())) == ("{{{{}}}}"));
}
