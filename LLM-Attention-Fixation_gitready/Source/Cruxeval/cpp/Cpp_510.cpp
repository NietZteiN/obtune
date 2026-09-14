#include<assert.h>
#include<bits/stdc++.h>
union Union_long_float{
    long f0;
    float f1;    Union_long_float(long _f0) : f0(_f0) {}
    Union_long_float(float _f1) : f1(_f1) {}
    ~Union_long_float() {}
    bool operator==(long f) {
        return f0 == f ;
    }    bool operator==(float f) {
        return f1 == f ;
    }
};
union Union_std_string_long{
    std::string f0;
    long f1;    Union_std_string_long(std::string _f0) : f0(_f0) {}
    Union_std_string_long(long _f1) : f1(_f1) {}
    ~Union_std_string_long() {}
    bool operator==(std::string f) {
        return f0 == f ;
    }    bool operator==(long f) {
        return f1 == f ;
    }
};
Union_std_string_long f(std::map<long,std::string> a, long b, std::string c, std::string d, Union_long_float e) {
    std::string key = d;
    std::string num;
    if (a.find(b) != a.end()) {
        num = a[b];
        a.erase(b);
    }
    if (b > 3) {
        return Union_std_string_long(c);
    } else {
        return Union_std_string_long(std::stol(num));
    }
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<long,std::string>({{7, "ii5p"}, {1, "o3Jwus"}, {3, "lot9L"}, {2, "04g"}, {9, "Wjf"}, {8, "5b"}, {0, "te6"}, {5, "flLO"}, {6, "jq"}, {4, "vfa0tW"}})), (4), ("Wy"), ("Wy"), (1.0f)) == ("Wy"));
}
