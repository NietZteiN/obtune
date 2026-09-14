#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::vector<std::string> a;
    std::stringstream ss(text);
    std::string line;
    while (std::getline(ss, line, '\n')) {
        a.push_back(line);
    }
    
    std::vector<std::string> b;
    for (size_t i = 0; i < a.size(); ++i) {
        std::string c = a[i];
        size_t pos = c.find('\t');
        while (pos != std::string::npos) {
            c.replace(pos, 1, "    ");
            pos = c.find('\t', pos + 4);  // Move past the replaced "    "
        }
        b.push_back(c);
    }
    
    return std::accumulate(b.begin(), b.end(), std::string{}, [](std::string result, std::string next) {
        return result.empty() ? next : result + "\n" + next;
    });
}
int main() {
    auto candidate = f;
    assert(candidate(("			tab tab tabulates")) == ("            tab tab tabulates"));
}
