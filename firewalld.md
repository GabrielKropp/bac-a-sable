# Firewalld

## Principe de fonctionnement:
Utilisation de zones selon le niveau de confiance du réseau sur lequel on est.
Une zone peut être 1 to X networks, 1 to X interface(s)
Et on ouvre 
* des services (ssh, ntp, …)
* Des ports spécifiques
* Voire des rules custom (rich rules)

# Le point de vue RedHat : firewalld VS iptables VS nftables
The following is a brief overview in which scenario you should use one of the following utilities:

* firewalld: Use the firewalld utility for simple firewall use cases. The utility is easy to use and covers the typical use cases for these scenarios.
* nftables: Use the nftables utility to set up complex and performance-critical firewalls, such as for a whole network.
* iptables: The iptables utility on Red Hat Enterprise Linux uses the nf_tables kernel API instead of the legacy back end. The nf_tables API provides backward compatibility so that scripts that use iptables commands still work on Red Hat Enterprise Linux. For new firewall scripts, Red Hat recommends to use nftables.

### Zones par défaut : 
* drop : le niveau de confiance le plus bas. Toutes les connexions entrantes sont interrompues sans réponse et seules les connexions sortantes sont possibles.
* block : similaire à ce qui précède, mais au lieu de simplement interrompre les connexions, les demandes entrantes sont rejetées avec un message icmp-host-prohibited ou icmp6-adm-prohibited.
* public : représente les réseaux publics, non fiables. Vous ne faites pas confiance aux autres ordinateurs, mais vous pouvez autoriser certaines connexions entrantes au cas par cas.
* external : les réseaux externes dans l’éventualité où vous utilisez le pare-feu comme passerelle. Il est configuré pour le masquage NAT de sorte que votre réseau interne reste privé mais accessible.
* interne : l’autre côté de la zone externe, utilisé pour la partie interne d’une passerelle. Les ordinateurs sont assez fiables et certains services supplémentaires sont disponibles.
* dmz : utilisé pour les ordinateurs situés dans un DMZ (ordinateurs isolés qui n’auront pas accès au reste de votre réseau). Seules certaines connexions entrantes sont autorisées.
* work : utilisé pour les machines de travail. Fait confiance à la plupart des ordinateurs du réseau. Quelques services supplémentaires pourraient être autorisés.
* home : un environnement domestique. Cela implique généralement que vous faites confiance à la plupart des autres ordinateurs et que quelques services supplémentaires seront acceptés.
* trusted : fais confiance à toutes les machines du réseau. La plus ouverte des options disponibles et doit être utilisée avec parcimonie.

La « public » est la plus proche de la philosophie DINUM.

### Généralités:
* Bien mettre la zone lors d’une création de règle.
* Définir une zone par défaut. Ca y collera toutes les interfaces et règles si aucun paramètre n’est donné.
* Penser au —permanent

### Zones VS interfaces
Active zones fulfill two different roles. Zones with associated interface(s) act as interface zones, and zones with associated source(s) act as source zones (a zone could fulfill both roles). Firewalld handles a packet in the following order:
1. The corresponding source zone. Zero or one such zones may exist. If the source zone deals with the packet because the packet satisfies a rich rule, the service is whitelisted, or the target is not default, we end here. Otherwise, we pass the packet on.
2. The corresponding interface zone. Exactly one such zone will always exist. If the interface zone deals with the packet, we end here. Otherwise, we pass the packet on.
3. The firewalld default action. Accept icmp packets and reject everything else.



## Idée 1.1 : coller à iptables, version rich rules
Via iptables on filtre finement sur source/destination/ports

Note : pas vu de notion de destination dans les rich rules. Suppose que la destination = la zone dans laquelle est créée la règle = toutes les interfaces qui sont dedans.

Pour cela, créer une zone par interface (une zone admin, une zone service).  Mettre la zone service en zone par défaut.
Utiliser les rich rules et non les services lorsqu’on souhaite filtrer les source IP
-> les rich rules ne sont pas intuitives.

## Idée 1.2 : coller à iptables, version multizones
On peut créer autant de zones que de « sources IP » qu’on veut filtrer.
Ex: une zone métrologie, avec les IPs des serveurs de métrologie en source + ouverture des services correspondants (node-exporter, cadvisor etc …). Rich rules if required
Puis une zone admin et une zone service pour coller à tout traffic plus « global » lié à ces interfaces réseaux (où on y mettrait les interfaces de la machine). Rich rules if required


## Idée 2 : philosophie firewalld simple
On ouvre que le nécessaire, sans les source IP, mais en respectant admin et service

Pour cela, créer une zone par interface (une zone admin, une zone service). Mettre la zone service en zone par défaut.

Ouvrir les services et ports adéquats selon le serveur (dans les différents ansible) en pointant bien la zone correspondante.
Moins précis, mais simple.

## Idée 3: zone public
Le plus simple, utiliser la zone public, la mettre en défaut, et ouvrir les services / ports correspondants. Ca supprime la distinction admin/service (au sens règle FW) mais évite la création de zone custom, donc plus simple à mettre en oeuvre.
