#include<assert.h>
#include<bits/stdc++.h>
std::tuple<std::string, std::string> f(std::string text) {
    std::string topic, problem;
    size_t pos = text.rfind('|');
    if (pos != std::string::npos) {
        topic = text.substr(0, pos);
        problem = text.substr(pos + 1, std::string::npos);
    } else {
        topic = "";
        problem = text;
    }
    if (problem == "r") {
        std::replace(problem.begin(), problem.end(), 'u', 'p');
    }
    return std::make_tuple(topic, problem);
}
int main() {
    auto candidate = f;
    assert(candidate(("|xduaisf")) == (std::make_tuple("", "xduaisf")));
}
