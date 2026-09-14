using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static float F(float price, string product) {
        List<string> inventory = new List<string> { "olives", "key", "orange" };
        if (!inventory.Contains(product)) {
            return price;
        } else {
            price *= 0.85f;
            inventory.Remove(product);
        }
        return price;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((8.5f), ("grapes")) == (8.5f));
    }

}
