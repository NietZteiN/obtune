#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string name) {
    std::stringstream ss;
    ss << "| ";
    std::istringstream iss(name);
    std::string word;
    while (iss >> word) {
        ss << word << " ";
    }
    ss << "|";
    return ss.str();
}
int main() {
    auto candidate = f;
    assert(candidate(("i am your father")) == ("| i am your father |"));
}
